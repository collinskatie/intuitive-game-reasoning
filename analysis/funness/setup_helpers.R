# ==============================================================================
# Shared setup, constants, and helper functions for the funness analyses.

# Help from Claude Code for refactor

# Key entry points for plugging in a new model's predictions:
#
#   df       <- prepare_funness_data("path/to/new_model.csv")
#   result   <- fit_funness_model(df)              # or fit_funness_model("path/...csv")
#   print_coefs(result$coefs)
#   summary_funness_fit(result)                    # prints R^2 + coefs together
# The CSV must have columns: game_id, emd, challenge, len, humans
# (humans is a stringified python list, one entry per participant)
# ==============================================================================

# --- Libraries ---------------------------------------------------------------
suppressPackageStartupMessages({
  library(tidyverse)
  library(jsonlite)
  library(knitr)
  library(kableExtra)
  library(xtable)
})
# ggpattern is optional (only used for hatched bars in generalization_test.R)
if (requireNamespace("ggpattern", quietly = TRUE)) library(ggpattern)

set.seed(7)

# --- File paths --------------------------------------------------------------
# These scripts are expected to be run from analysis/funness/ as the working
# directory. Adjust the prefixes here if you relocate the scripts.
FEATURE_FILES <- list(
  Novice = "../../model-data/local_model_readout_fun_features.csv",
  Expert = "../../model-data/expert_model_readout_fun_features.csv",
  Random = "../../model-data/random_model_readout_fun_features.csv"
)

META_FILES <- list(
  game2game_type = "../game_info/game2game_type.json",
  game2idx       = "../game_info/game2idx.json",
  game_stimuli   = "../game_info/game_stimuli.json"
)

POST_PLAY_FILE <- "../../human-data/play-exp/play_human_fun.json"

# --- Constants ---------------------------------------------------------------
GAME_TRAITS <- c(
  "largerthan3x3board",
  "diff3inrow",
  "nonsquareboard",
  "asymmetricwin",
  "asymmetricplay",
  "constrainedwin",
  "misere"
)

GAME_TRAITS_PRETTY <- c(
  largerthan3x3board = "Board > 3x3",
  diff3inrow         = "K != 3",
  nonsquareboard     = "Non-square Board",
  asymmetricwin      = "Asymmetric Win",
  asymmetricplay     = "Asymmetric Play",
  constrainedwin     = "Constrained Win",
  misere             = "Misère"
)

PARAM_NAME_MAP <- c(
  "(Intercept)"                = "Intercept",
  "emd"                        = "Balance",
  "challenge"                  = "Challenge",
  "poly(len, 2, raw = TRUE)1"  = "Game Length (Linear)",
  "poly(len, 2, raw = TRUE)2"  = "Game Length (Quadratic)",
  "board_size"                 = "Board Size",
  "special_trait_counts"       = "Number of Special Traits",
  "num_constraints"            = "Number of Constraints"
)

# Standard formulas
FORMULA_BASE_LIN  <- humans_mean ~ emd + challenge + len
FORMULA_BASE_QUAD <- humans_mean ~ emd + challenge + poly(len, 2, raw = TRUE)


# --- Parsing -----------------------------------------------------------------
parse_python_list_mean <- function(s) {
  if (length(s) != 1 || is.na(s) || s == "") return(NA_real_)
  clean <- gsub("\\[|\\]", "", s)
  nums  <- as.numeric(str_split(clean, ",", simplify = TRUE))
  mean(nums, na.rm = TRUE)
}

parse_python_list <- function(s) {
  if (is.na(s) || s == "") return(numeric())
  as.numeric(strsplit(gsub("\\[|\\]", "", s), ",")[[1]])
}


# --- Game features -----------------------------------------------------------
compute_board_size <- function(id, stimuli) {
  obj <- stimuli[[id]]
  if (is.null(obj$`board-x`) || is.null(obj$`board-y`)) return(NA_real_)
  obj$`board-x` * obj$`board-y`
}

compute_win_cond <- function(id, stimuli) {
  obj <- stimuli[[id]]
  obj$N %||% NA_real_
}

get_game_characteristics <- function(id, types, stimuli) {
  if (!id %in% names(types)) {
    return(list(traits = rep(NA_integer_, length(GAME_TRAITS)),
                special_count = NA_integer_, num_constraints = NA_integer_))
  }
  type     <- types[[id]]
  obj      <- stimuli[[id]]
  board_sz <- obj$`board-x` * obj$`board-y`
  K        <- obj$N

  flags <- c(
    as.integer(board_sz > 9),
    as.integer(K != 3),
    as.integer(type == "rectangle-board"),
    as.integer(type %in% c("player1-constraintA", "player1-constraintB", "diff-win")),
    as.integer(type %in% c("player1-2pieces", "player2-2pieces")),
    as.integer(type %in% c("only-diag", "no-diag",
                           "player1-constraintA", "player1-constraintB")),
    as.integer(type == "loss")
  )
  list(traits          = flags,
       special_count   = sum(flags),
       num_constraints = flags[4] + flags[6])
}

add_game_features <- function(df, types, stimuli) {
  if (!"game_id" %in% names(df)) return(df)

  ch <- map(df$game_id, ~ get_game_characteristics(.x, types, stimuli))

  df <- df %>%
    mutate(
      board_size           = map_dbl(game_id, compute_board_size, stimuli),
      win_condition        = map_dbl(game_id, compute_win_cond, stimuli),
      special_trait_counts = map_int(ch, "special_count"),
      num_constraints      = map_int(ch, "num_constraints")
    )

  for (i in seq_along(GAME_TRAITS)) {
    trait <- GAME_TRAITS[i]
    df[[trait]] <- map_int(ch, ~ .x$traits[i])
  }
  df
}


# --- Main data-preparation pipeline ------------------------------------------
# One entry point: take a path to a model-features CSV (or an already-loaded
# tibble with the same columns) and return a tidy df ready for funness
# regressions. Scaling is per-dataset, matching the published analyses.
prepare_funness_data <- function(csv_path_or_df, types = NULL, stimuli = NULL,
                                 drop_infinite = TRUE) {
  if (is.null(types))   types   <- read_json(META_FILES$game2game_type)
  if (is.null(stimuli)) stimuli <- read_json(META_FILES$game_stimuli)

  df <- if (is.character(csv_path_or_df)) {
    read_csv(csv_path_or_df, show_col_types = FALSE)
  } else {
    csv_path_or_df
  }
  if (drop_infinite) df <- df %>% filter(!str_starts(game_id, "inf"))

  df <- df %>%
    mutate(
      humans_mean   = map_dbl(humans, parse_python_list_mean),
      humans_parsed = map(humans, parse_python_list)
    ) %>%
    add_game_features(types, stimuli) %>%
    mutate(
      emd_unscaled       = emd,
      challenge_unscaled = challenge,
      len_unscaled       = len
    )

  # Per-game bootstrap CI on the human mean (for scatter error bars)
  df <- df %>%
    mutate(
      ci_vals = map(humans_parsed, bootstrap_mean_ci),
      ymin    = map_dbl(ci_vals, "lower"),
      ymax    = map_dbl(ci_vals, "upper")
    ) %>%
    select(-ci_vals)

  # Scale the predictors used by the funness regression
  df$emd       <- as.numeric(scale(df$emd))
  df$challenge <- as.numeric(scale(df$challenge))
  df$len       <- as.numeric(scale(df$len))

  df
}


# --- Bootstrap helpers -------------------------------------------------------
# Three distinct flavors; choose by what you are asking.
#
#   bootstrap_mean_ci()      : CI of the mean of a vector (e.g. humans for one game).
#   bootstrap_r2_resample()  : in-sample R^2; humans are resampled per game, model
#                              predictions are FIXED. Used for scatter R^2 labels.
#   bootstrap_r2_splithalf() : held-out R^2; the model is refit on 50% of games
#                              and evaluated on the other 50%. Used for the
#                              generalization test (ED Fig 4c).

bootstrap_mean_ci <- function(x, n_boot = 1000) {
  x <- x[!is.na(x)]
  if (length(x) == 0) return(c(lower = NA_real_, mean = NA_real_, upper = NA_real_))
  boot <- replicate(n_boot, mean(sample(x, replace = TRUE)))
  qs   <- quantile(boot, c(0.025, 0.5, 0.975), na.rm = TRUE)
  c(lower = unname(qs[1]), mean = unname(qs[2]), upper = unname(qs[3]))
}

bootstrap_r2_resample <- function(model, df, n_boot = 1000) {
  preds <- predict(model)
  humans_per_game <- map(df$humans_parsed, ~ .x[!is.na(.x)])

  r2_vals <- replicate(n_boot, {
    boot_means <- map_dbl(humans_per_game,
                          ~ if (length(.x) == 0) NA_real_ else mean(sample(.x, replace = TRUE)))
    if (any(is.na(boot_means)) || sd(boot_means, na.rm = TRUE) == 0) return(NA_real_)
    cor(boot_means, preds, use = "complete.obs")^2
  })
  r2_vals <- r2_vals[!is.na(r2_vals)]
  if (length(r2_vals) == 0) return(c(lower = NA_real_, mean = NA_real_, upper = NA_real_))
  c(lower = unname(quantile(r2_vals, 0.025)),
    mean  = mean(r2_vals),
    upper = unname(quantile(r2_vals, 0.975)))
}

bootstrap_r2_splithalf <- function(formula, data, B = 500) {
  vars <- all.vars(formula)
  r2s <- replicate(B, {
    idx   <- sample(nrow(data))
    split <- floor(nrow(data) / 2)
    train <- data[idx[1:split], ]     %>% drop_na(all_of(vars))
    test  <- data[idx[-(1:split)], ]  %>% drop_na(all_of(vars))
    if (nrow(train) == 0 || nrow(test) == 0) return(NA_real_)
    model <- tryCatch(lm(formula, data = train), error = function(e) NULL)
    if (is.null(model)) return(NA_real_)
    cor(predict(model, newdata = test), test$humans_mean, use = "complete.obs")^2
  })
  list(mean_r2  = mean(r2s, na.rm = TRUE),
       ci_lower = unname(quantile(r2s, 0.025, na.rm = TRUE)),
       ci_upper = unname(quantile(r2s, 0.975, na.rm = TRUE)))
}

# Bootstrap coefficients by resampling humans per game.
# Use this for "within-rating" uncertainty (intuitive gamer quadratic baseline,
# post-play coefs, the just-think-vs-postplay density plot).
bootstrap_coefs <- function(formula, df, n_boot = 1000) {
  humans_per_game <- df$humans_parsed
  all_names <- names(coef(lm(formula, data = df)))

  mat <- replicate(n_boot, {
    boot_means <- map_dbl(humans_per_game, function(r) {
      r <- r[!is.na(r)]
      if (length(r) == 0) return(NA_real_)
      mean(sample(r, replace = TRUE))
    })
    boot_df <- df; boot_df$humans_mean <- boot_means
    fit <- tryCatch(lm(formula, data = boot_df), error = function(e) NULL)
    out <- rep(NA_real_, length(all_names)); names(out) <- all_names
    if (!is.null(fit)) out[names(coef(fit))] <- coef(fit)
    out
  })
  as_tibble(t(mat))
}

# Bootstrap coefficients by resampling games (rows) with replacement.
# Use this for the cross-agent / model-comparison analysis in
# generalization_test.R, where the relevant uncertainty is over which games
# we'd see, not over rating noise within a fixed game set.
bootstrap_coefs_by_games <- function(formula, df, n_boot = 1000) {
  all_names <- names(coef(lm(formula, data = df)))
  n <- nrow(df)

  mat <- replicate(n_boot, {
    boot_df <- df[sample(n, replace = TRUE), , drop = FALSE]
    fit <- tryCatch(lm(formula, data = boot_df), error = function(e) NULL)
    out <- rep(NA_real_, length(all_names)); names(out) <- all_names
    if (!is.null(fit)) out[names(coef(fit))] <- coef(fit)
    out
  })
  as_tibble(t(mat))
}

# Map raw lm coefficient names to display names; falls back through
# PARAM_NAME_MAP, then GAME_TRAITS_PRETTY, then the raw name.
rename_param <- function(p) {
  dplyr::coalesce(unname(PARAM_NAME_MAP[p]),
                  unname(GAME_TRAITS_PRETTY[p]),
                  p)
}

# Summarize coefficient bootstrap samples to mean + 95% CI.
summarize_coef_samples <- function(samples) {
  samples %>%
    pivot_longer(everything(), names_to = "Parameter", values_to = "Estimate") %>%
    group_by(Parameter) %>%
    summarise(lower = quantile(Estimate, 0.025, na.rm = TRUE),
              mean  = mean(Estimate, na.rm = TRUE),
              upper = quantile(Estimate, 0.975, na.rm = TRUE),
              .groups = "drop") %>%
    mutate(Parameter = rename_param(Parameter))
}

# Per-game prediction CI (horizontal error bars on scatter plots).
bootstrap_prediction_ci <- function(formula, df, n_boot = 1000) {
  humans_per_game <- df$humans_parsed
  pred_mat <- matrix(NA_real_, nrow = n_boot, ncol = nrow(df))

  for (b in seq_len(n_boot)) {
    boot_means <- map_dbl(humans_per_game, function(r) {
      r <- r[!is.na(r)]
      if (length(r) == 0) return(NA_real_)
      mean(sample(r, replace = TRUE))
    })
    boot_df <- df; boot_df$humans_mean <- boot_means
    fit <- tryCatch(lm(formula, data = boot_df), error = function(e) NULL)
    if (!is.null(fit)) pred_mat[b, ] <- predict(fit, newdata = df)
  }

  tibble(
    game_id    = df$game_id,
    pred_lower = apply(pred_mat, 2, quantile, 0.025, na.rm = TRUE),
    pred_mean  = apply(pred_mat, 2, quantile, 0.500, na.rm = TRUE),
    pred_upper = apply(pred_mat, 2, quantile, 0.975, na.rm = TRUE)
  )
}


# --- High-level "plug in a CSV" wrapper --------------------------------------
# Fit the base quadratic funness model and bootstrap everything in one shot.
# Accepts either a prepared df or a CSV path.
fit_funness_model <- function(df_or_path, formula = FORMULA_BASE_QUAD,
                              n_boot = 1000) {
  df <- if (is.character(df_or_path)) prepare_funness_data(df_or_path) else df_or_path

  model   <- lm(formula, data = df)
  r2      <- bootstrap_r2_resample(model, df, n_boot = n_boot)
  samples <- bootstrap_coefs(formula, df, n_boot = n_boot)

  list(model        = model,
       formula      = formula,
       df           = df,
       r2           = r2,
       coef_samples = samples,
       coefs        = summarize_coef_samples(samples))
}

print_coefs <- function(coefs_tbl, digits = 3) {
  coefs_tbl %>%
    mutate(`Estimate (95% CI)` = sprintf("%.*f (%.*f, %.*f)",
                                         digits, mean, digits, lower, digits, upper)) %>%
    select(Parameter, `Estimate (95% CI)`)
}

summary_funness_fit <- function(result) {
  cat(sprintf("R² = %.3f (%.3f, %.3f)\n",
              result$r2["mean"], result$r2["lower"], result$r2["upper"]))
  cat("Coefficients (mean, 95% CI):\n")
  print(print_coefs(result$coefs))
  invisible(result)
}


# --- Tables ------------------------------------------------------------------
# Generic ANOVA comparison: each alt model vs the base.
make_anova_comparison_table <- function(base_model, alt_models, labels,
                                        col_label = "Comparison",
                                        caption   = "ANOVA comparison") {
  results <- map2_dfr(alt_models, labels, ~ {
    an <- anova(base_model, .x)
    diff_row <- an[2, ]
    tibble(
      label         = .y,
      `F-statistic` = round(diff_row$F, 3),
      `p-value`     = formatC(diff_row$`Pr(>F)`, format = "e", digits = 2),
      `AIC-base`    = round(AIC(base_model), 1),
      `AIC-alt`     = round(AIC(.x), 1)
    )
  })
  results %>%
    kbl(format = "latex", booktabs = TRUE,
        col.names = c(col_label, "F", "p", "AIC (Base)", "AIC (Alt)"),
        align = "lcccc", caption = caption) %>%
    kable_styling(latex_options = "hold_position")
}

write_coefs_latex <- function(coefs_summary, path, caption, label) {
  tbl <- coefs_summary %>%
    mutate(`Estimate (95\\% CI)` = sprintf("%.3f (%.3f, %.3f)", mean, lower, upper)) %>%
    select(Parameter, `Estimate (95\\% CI)`)
  if (!dir.exists(dirname(path))) dir.create(dirname(path), recursive = TRUE)
  xt <- xtable(tbl, caption = caption, label = label)
  print(xt, include.rownames = FALSE, booktabs = TRUE,
        sanitize.text.function = identity, file = path)
  invisible(tbl)
}


# --- Plotting ----------------------------------------------------------------
# Single-predictor scatter (used for just-emd, just-challenge, just-len).
plot_simple_predictor <- function(df, model, xvar_unscaled, xlabel,
                                  quadratic   = FALSE,
                                  xlim_bounds = NULL,
                                  output_path = NULL) {
  r2 <- bootstrap_r2_resample(model, df, n_boot = 1000)
  r2_label <- sprintf("R² = %.2f (%.2f, %.2f)", r2["mean"], r2["lower"], r2["upper"])

  smooth_form <- if (quadratic) y ~ poly(x, 2, raw = TRUE) else y ~ x

  p <- ggplot(df, aes(x = .data[[xvar_unscaled]], y = humans_mean)) +
    geom_point(size = 3, alpha = 0.7) +
    geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.1,
                  size = 1.1, alpha = 0.2) +
    stat_smooth(method = "lm", formula = smooth_form, se = TRUE, color = "grey") +
    theme_classic(base_size = 16) +
    labs(title = r2_label, x = xlabel, y = "Human Funness") +
    theme(plot.title  = element_text(hjust = 0.5, size = 26, face = "bold"),
          axis.title  = element_text(size = 24),
          axis.text   = element_text(size = 18))
  if (!is.null(xlim_bounds)) p <- p + xlim(xlim_bounds[1], xlim_bounds[2])

  if (!is.null(output_path)) {
    if (!dir.exists(dirname(output_path))) dir.create(dirname(output_path), recursive = TRUE)
    ggsave(output_path, plot = p, width = 6, height = 5, dpi = 300)
  }
  invisible(p)
}

# Predicted-vs-human scatter, with optional highlighted game subsets.
# `highlights` is an optional list with names "top", "bottom", "other";
# each is a character vector of game_ids to overlay with a circle outline.
plot_predicted_vs_human <- function(df, model,
                                    highlights  = NULL,
                                    point_color = "red",
                                    output_path = NULL) {
  r2 <- bootstrap_r2_resample(model, df, n_boot = 1000)
  r2_label <- sprintf("R² = %.2f (%.2f, %.2f)", r2["mean"], r2["lower"], r2["upper"])

  boot_preds <- bootstrap_prediction_ci(formula(model), df)
  df2 <- df %>%
    mutate(predicted = predict(model)) %>%
    left_join(boot_preds, by = "game_id")

  p <- ggplot(df2, aes(x = predicted, y = humans_mean)) +
    geom_point(size = 3, alpha = 0.7, color = point_color) +
    geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.1, size = 1.1,
                  alpha = 0.2, color = point_color) +
    geom_errorbarh(aes(xmin = pred_lower, xmax = pred_upper), height = 0.1,
                   size = 1.1, alpha = 0.2, color = point_color) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey") +
    theme_classic(base_size = 16) +
    labs(title = r2_label, x = "Model", y = "Human Funness") +
    theme(plot.title = element_text(hjust = 0.5, size = 26, face = "bold"),
          axis.title = element_text(size = 24),
          axis.text  = element_text(size = 18))

  # Outline circles for highlighted points; black for top/bottom, purple for other.
  if (!is.null(highlights)) {
    add_outline <- function(p, ids, color) {
      if (length(ids) == 0) return(p)
      sub <- df2 %>% filter(game_id %in% ids)
      if (nrow(sub) == 0) return(p)
      p + geom_point(data = sub, aes(x = predicted, y = humans_mean),
                     shape = 21, size = 6, stroke = 1.5, color = color, fill = NA)
    }
    p <- add_outline(p, c(highlights$top %||% character(0),
                          highlights$bottom %||% character(0)), "black")
    p <- add_outline(p, highlights$other %||% character(0), "purple")
  }

  if (!is.null(output_path)) {
    if (!dir.exists(dirname(output_path))) dir.create(dirname(output_path), recursive = TRUE)
    ggsave(output_path, plot = p, width = 6, height = 5, dpi = 300)
  }
  invisible(p)
}

# Export scatter data to CSV (for downstream plotting, e.g. in Python).
export_scatter_data <- function(df, model = NULL, x_col = NULL, path) {
  if (!dir.exists(dirname(path))) dir.create(dirname(path), recursive = TRUE)
  if (is.null(model)) {
    out <- df %>% select(game_id, x = all_of(x_col),
                         human_mean = humans_mean,
                         human_ci_lower = ymin, human_ci_upper = ymax)
  } else {
    boot <- bootstrap_prediction_ci(formula(model), df)
    out <- df %>%
      mutate(predicted = predict(model)) %>%
      left_join(boot, by = "game_id") %>%
      select(game_id,
             model_prediction = predicted,
             model_ci_lower   = pred_lower,
             model_ci_upper   = pred_upper,
             human_mean       = humans_mean,
             human_ci_lower   = ymin,
             human_ci_upper   = ymax)
  }
  write_csv(out, path)
  invisible(out)
}
