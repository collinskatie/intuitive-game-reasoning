# ==============================================================================
# Generalization test on model comparison

# Help from Claude Code for refactor
# ==============================================================================
setwd("~/intuitive-game-reasoning/analysis/funness/")
source("setup_helpers.R")

for (d in c("plots", "fig_data_files", "tables", "predictions")) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE)
}


# --- load all agent feature CSVs ---------------------------------------------
types   <- read_json(META_FILES$game2game_type)
stimuli <- read_json(META_FILES$game_stimuli)

gamer_dfs <- list(
  Novice = prepare_funness_data(FEATURE_FILES$Novice, types, stimuli),
  Expert = prepare_funness_data(FEATURE_FILES$Expert, types, stimuli),
  Random = prepare_funness_data(FEATURE_FILES$Random, types, stimuli)
)


gamer_dfs <- map(gamer_dfs, function(df) {
  df %>% mutate(across(c(board_size, special_trait_counts, num_constraints),
                       ~ as.numeric(scale(.x))))
})


formulas <- list(
  QuadBaseline = FORMULA_BASE_QUAD,
  TraitsOnly   = as.formula(paste("humans_mean ~", paste(GAME_TRAITS, collapse = " + "))),
  FeaturesOnly = as.formula("humans_mean ~ board_size + special_trait_counts + num_constraints")
)


# --- run analysis per variant ------------------------------------------------
analyze_variant <- function(df, label) {
  message("Running analysis for ", label)

  r2_rows <- imap_dfr(formulas, function(f, fname) {
    res <- bootstrap_r2_splithalf(f, df, B = 500)
    tibble(Model = fname, Mean_R2 = res$mean_r2,
           CI_Lower = res$ci_lower, CI_Upper = res$ci_upper,
           Dataset = label)
  })

  # coefficients here are bootstrapped by resampling games (rows) with
  # replacement
  coef_rows <- imap_dfr(formulas, function(f, fname) {
    summarize_coef_samples(bootstrap_coefs_by_games(f, df, n_boot = 500)) %>%
      mutate(Model = fname, Dataset = label)
  })

  list(r2 = r2_rows, coefs = coef_rows)
}

analysis_results <- imap(gamer_dfs, ~ analyze_variant(.x, .y))
r2_results       <- map_dfr(analysis_results, "r2") %>%
  mutate(Model = factor(Model, levels = c("QuadBaseline", "TraitsOnly", "FeaturesOnly")))
coef_results     <- map_dfr(analysis_results, "coefs")


# --- comparison barplot -----------------------------

quad_df <- r2_results %>%
  filter(Model == "QuadBaseline") %>%
  transmute(Category = Dataset, Mean_R2, CI_Lower, CI_Upper)

avg_for <- function(model_name, label) {
  r2_results %>%
    filter(Model == model_name) %>%
    summarise(Mean_R2  = mean(Mean_R2),
              CI_Lower = mean(CI_Lower),
              CI_Upper = mean(CI_Upper)) %>%
    mutate(Category = label)
}

plot_df <- bind_rows(
  quad_df,
  avg_for("TraitsOnly",   "Binary Game Traits"),
  avg_for("FeaturesOnly", "Agg Game Traits")
) %>%
  mutate(
    Category = recode(as.character(Category),
                      "Novice" = "Intuitive\nGamer",
                      "Expert" = "Expert\nGamer",
                      "Random" = "Random\nGamer",
                      "Binary Game Traits" = "Binary\nTraits",
                      "Agg Game Traits"    = "Agg\nFeatures"),
    Category = factor(Category, levels = c("Intuitive\nGamer", "Expert\nGamer", "Random\nGamer",
                                           "Binary\nTraits", "Agg\nFeatures"))
  )

write_csv(
  plot_df %>% mutate(category = gsub("\n", " ", as.character(Category))) %>%
    select(category, mean_r2 = Mean_R2, ci_lower = CI_Lower, ci_upper = CI_Upper),
  "fig_data_files/fig4_compare_barplot_data.csv"
)

plot_bar <- ggplot(plot_df, aes(x = Category, y = Mean_R2, fill = Category)) +
  geom_col(width = 0.7) +
  geom_errorbar(aes(ymin = CI_Lower, ymax = CI_Upper), width = 0.2) +
  scale_fill_manual(values = c(
    "Intuitive\nGamer" = "#FF0000",
    "Expert\nGamer"    = "#0000FF",
    "Random\nGamer"    = "#808080",
    "Binary\nTraits"   = "#FFA500",
    "Agg\nFeatures"    = "yellow"
  )) +
  scale_x_discrete(expand = c(0, 0.01)) +
  theme_minimal(base_size = 14) +
  theme(legend.position  = "none",
        axis.text.x      = element_text(size = 18, lineheight = 0.9),
        axis.text.y      = element_text(size = 16),
        axis.title.y     = element_text(size = 16),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        plot.margin      = margin(10, 10, 10, 10)) +
  labs(x = NULL, y = expression(R^2))

ggsave("plots/r2_comparison_barplot.png", plot_bar, width = 5, height = 5, dpi = 300)
print(plot_bar)


# --- LaTeX coefficient tables ---------------------
write_novice_coefs <- function(model_name, file_label) {
  tbl <- coef_results %>%
    filter(Dataset == "Novice", Model == model_name)

  out_stem <- paste0("tables/novice_", tolower(gsub("[^a-zA-Z]+", "_", file_label)))
  write_coefs_latex(tbl,
                    path    = paste0(out_stem, ".tex"),
                    caption = paste0(file_label, " (Intuitive Gamer) -- Bootstrapped Coefficients"),
                    label   = paste0("tab:", tolower(gsub(" ", "_", file_label)), "_novice"))
  write_csv(tbl, paste0(out_stem, ".csv"))
  invisible(tbl)
}

write_novice_coefs("QuadBaseline", "Quadratic Baseline")
write_novice_coefs("TraitsOnly",   "Binary Game Traits")
write_novice_coefs("FeaturesOnly", "Agg Game Traits")


# --- save bootstrap-averaged predictions per (variant, model) ----------------
bootstrap_predictions_avg <- function(formula, data, B = 500) {
  preds_list <- map(seq_len(B), function(i) {
    idx <- sample(nrow(data), replace = TRUE)
    fit <- tryCatch(lm(formula, data = data[idx, ]), error = function(e) NULL)
    if (is.null(fit)) return(rep(NA_real_, nrow(data)))
    predict(fit, newdata = data)
  })
  tibble(game_id        = data$game_id,
         avg_prediction = rowMeans(do.call(cbind, preds_list), na.rm = TRUE))
}

for (variant in names(gamer_dfs)) {
  for (mname in names(formulas)) {
    preds_tbl <- bootstrap_predictions_avg(formulas[[mname]], gamer_dfs[[variant]], B = 500)
    write_csv(preds_tbl,
              file.path("predictions",
                        paste0(tolower(variant), "_", tolower(mname), "_predictions.csv")))
  }
}


# --- "Simulation Only" vs "+ Novelty" comparison (Intuitive Gamer) -----------
novice_df <- gamer_dfs$Novice
form_novelty <- list(
  Baseline    = FORMULA_BASE_QUAD,
  LinearTrait = humans_mean ~ emd + challenge + poly(len, 2, raw = TRUE) + special_trait_counts,
  QuadTrait   = humans_mean ~ emd + challenge + poly(len, 2, raw = TRUE) +
                              poly(special_trait_counts, 2, raw = TRUE)
)
comp_results <- imap_dfr(form_novelty, ~ {
  res <- bootstrap_r2_splithalf(.x, novice_df, B = 500)
  tibble(Model = .y, Mean_R2 = res$mean_r2,
         CI_Lower = res$ci_lower, CI_Upper = res$ci_upper)
}) %>%
  mutate(Label = factor(c("Simulation Only", "+ Linear Novelty", "+ Quadratic Novelty"),
                        levels = c("Simulation Only", "+ Linear Novelty", "+ Quadratic Novelty")))

if (requireNamespace("ggpattern", quietly = TRUE)) {
  plot_comp <- ggplot(comp_results, aes(x = Label, y = Mean_R2)) +
    ggpattern::geom_col_pattern(
      aes(pattern = Label),
      colour = "black", fill = "grey80",
      pattern_fill = "black", pattern_color = "black",
      pattern_alpha = 0.8, pattern_density = 0.1, pattern_spacing = 0.02,
      width = 0.7
    ) +
    ggpattern::scale_pattern_manual(values = c("Simulation Only"     = "none",
                                               "+ Linear Novelty"    = "stripe",
                                               "+ Quadratic Novelty" = "crosshatch")) +
    geom_errorbar(aes(ymin = CI_Lower, ymax = CI_Upper), width = 0.2) +
    theme_minimal(base_size = 14) +
    theme(legend.position  = "none",
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank()) +
    labs(x = NULL, y = expression(R^2))
  ggsave("plots/novice_novelty_comparison.png", plot_comp, width = 8, height = 6, dpi = 300)
}

xtable(
  comp_results %>%
    mutate(R2_CI = sprintf("%.3f [%.3f, %.3f]", Mean_R2, CI_Lower, CI_Upper)) %>%
    select(`Model Variant` = Label, `$R^2$ [95\\% CI]` = R2_CI),
  caption = "Adding novelty features to the Intuitive Gamer base quadratic. $R^2$ is 50/50 split-half.",
  label   = "tab:novice_novelty_r2_table"
) %>%
  print(include.rownames = FALSE, booktabs = TRUE,
        sanitize.text.function = identity,
        file = "tables/novice_novelty_r2_table.tex")

cat("\nDone.\n")
