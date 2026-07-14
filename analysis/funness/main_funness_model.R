# ==============================================================================
# primary funness model comparisons

# help from Claude Code for refactor
# ==============================================================================

setwd("~/intuitive-game-reasoning/analysis/funness/")
source("setup_helpers.R")

# output dirs
for (d in c("plots", "plots/funness_models", "fig_data_files", "tables")) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE)
}


# --- loading -----------------------------------------------------------------
types     <- read_json(META_FILES$game2game_type)
stimuli   <- read_json(META_FILES$game_stimuli)
novice_df <- prepare_funness_data(FEATURE_FILES$Novice, types, stimuli)


# --- 10x10 K-variation (then compared in other notebook for ext data figure) --------------------------
# held-out predictions: the K-variation games are always in the test set;
# the remaining games are split 50/50 to fit the funness model.
bootstrap_preds_heldout <- function(formula, data, predict_ids, B = 500) {
  heldout <- data %>% filter(game_id %in% predict_ids)
  rest    <- data %>% filter(!game_id %in% predict_ids)

  mat <- matrix(NA_real_, nrow = B, ncol = length(predict_ids))
  colnames(mat) <- predict_ids

  for (b in seq_len(B)) {
    idx   <- sample(nrow(rest))
    train <- rest[idx[seq_len(floor(nrow(rest) / 2))], ]
    fit   <- tryCatch(lm(formula, data = train), error = function(e) NULL)
    if (is.null(fit)) next
    preds <- predict(fit, newdata = heldout)
    for (i in seq_along(predict_ids)) {
      j <- which(heldout$game_id == predict_ids[i])
      if (length(j) == 1) mat[b, i] <- preds[j]
    }
  }

  tibble(game_id    = predict_ids,
         pred_mean  = apply(mat, 2, mean,     na.rm = TRUE),
         pred_lower = apply(mat, 2, quantile, 0.025, na.rm = TRUE),
         pred_upper = apply(mat, 2, quantile, 0.975, na.rm = TRUE))
}

k_variation_df <- novice_df %>%
  filter(str_detect(game_id, "^10\\.0\\*10\\.0\\*\\d+ pieces in a row wins\\.$")) %>%
  mutate(K = as.numeric(str_extract(game_id, "(?<=10\\.0\\*10\\.0\\*)\\d+"))) %>%
  filter(K >= 2, K <= 10) %>%
  arrange(K)

k_boot_preds <- bootstrap_preds_heldout(
  formula     = FORMULA_BASE_QUAD,
  data        = novice_df,
  predict_ids = k_variation_df$game_id,
  B           = 1000
)
k_variation_df <- k_variation_df %>% left_join(k_boot_preds, by = "game_id")

write_csv(
  k_variation_df %>% select(game_id, K,
                            human_mean     = humans_mean,
                            human_ci_lower = ymin,
                            human_ci_upper = ymax,
                            model_mean     = pred_mean,
                            model_ci_lower = pred_lower,
                            model_ci_upper = pred_upper),
  "fig_data_files/K_variation_funness_predictions.csv"
)



# --- linear ablations (drop one feature) ----------------------------------
model_base_lin <- lm(FORMULA_BASE_LIN, data = novice_df)
just_emd       <- lm(humans_mean ~ emd,       data = novice_df)
just_challenge <- lm(humans_mean ~ challenge, data = novice_df)
just_len       <- lm(humans_mean ~ poly(len, 2, raw = TRUE), data = novice_df)

lin_drop <- list(
  emd       = lm(humans_mean ~ challenge + len, data = novice_df),
  challenge = lm(humans_mean ~ emd + len,       data = novice_df),
  len       = lm(humans_mean ~ emd + challenge, data = novice_df)
)

cat("\nLinear ablations (drop one feature):\n")
cat(make_anova_comparison_table(
  base_model = model_base_lin,
  alt_models = lin_drop,
  labels     = c("emd (Balance)", "challenge", "len"),
  col_label  = "Feature Removed",
  caption    = "ANOVA: Linear ablations"
))


# --- linear vs quadratic per predictor ------------------------------------
quad_alt <- list(
  emd       = lm(humans_mean ~ poly(emd, 2, raw = TRUE) + challenge + len, data = novice_df),
  challenge = lm(humans_mean ~ emd + poly(challenge, 2, raw = TRUE) + len, data = novice_df),
  len       = lm(humans_mean ~ emd + challenge + poly(len, 2, raw = TRUE), data = novice_df)
)

cat("\nLinear vs quadratic per predictor:\n")
cat(make_anova_comparison_table(
  base_model = model_base_lin,
  alt_models = quad_alt,
  labels     = c("emd", "challenge", "len"),
  col_label  = "Predictor",
  caption    = "ANOVA: linear vs quadratic per predictor"
))

# Final base quadratic + a check against a "double quadratic" (emd quadratic too)
model_base_quad   <- lm(FORMULA_BASE_QUAD, data = novice_df)
model_quad_double <- lm(humans_mean ~ poly(emd, 2, raw = TRUE) + challenge + poly(len, 2, raw = TRUE),
                        data = novice_df)

cat(sprintf("AIC base-quadratic = %.1f ; double-quadratic = %.1f\n",
            AIC(model_base_quad), AIC(model_quad_double)))


# --- decomp feature and agg plots ---------------------------------------------------
plot_simple_predictor(novice_df, just_emd,       "emd_unscaled",       "Balance",
                      quadratic = FALSE, xlim_bounds = c(-1.1, 0.1),
                      output_path = "plots/just-emd.svg")
plot_simple_predictor(novice_df, just_challenge, "challenge_unscaled", "Challenge",
                      quadratic = FALSE, xlim_bounds = c(0, 1.25),
                      output_path = "plots/just-challenge.svg")
plot_simple_predictor(novice_df, just_len,       "len_unscaled",       "Game Length",
                      quadratic = TRUE,  xlim_bounds = c(0, 105),
                      output_path = "plots/just-len.svg")
plot_predicted_vs_human(novice_df, model_base_lin,
                        output_path = "plots/model-base-lin.svg")
plot_predicted_vs_human(novice_df, model_base_quad,
                        output_path = "plots/model-base-quad.svg")

# Specific games for overlay plot
viz_games_top <- c(
  '10.0*10.0*4 pieces in a row wins.',
  '7.0*7.0*Each player needs 4 pieces in a row to win. The first player cannot win by making a diagonal row (only horizontal and vertical rows count), but the second player does not have this restriction.',
  '10.0*10.0*5 pieces in a row wins. The second player can place 2 pieces as their first move, while the first player can only place 1 piece as their first move.',
  '10.0*10.0*5 pieces in a row loses.',
  '4.0*9.0*4 pieces in a row wins.',
  '4.0*4.0*3 pieces in a row wins. However, a player can only win by making a diagonal row. Horizontal and vertical rows do not count.',
  '4.0*4.0*3 pieces in a row wins. However, a player cannot win by making a diagonal row. Only horizontal and vertical rows count.',
  '10.0*10.0*The first player needs 5 pieces in a row to win, but the second player only needs 4 pieces in a row to win.'
)
viz_games_bottom <- c(
  '4.0*6.0*5 pieces in a row wins.',
  '2.0*5.0*3 pieces in a row wins.',
  '3.0*3.0*The first player needs 3 pieces in a row to win, but the second player only needs 2 pieces in a row to win.',
  '1.0*5.0*3 pieces in a row wins.'
)
plot_predicted_vs_human(
  novice_df, model_base_quad,
  highlights  = list(top = viz_games_top, bottom = viz_games_bottom),
  output_path = "plots/model-base-quad-highlighted.svg"
)

# Interactive plot for debugging and exploration
if (requireNamespace("plotly", quietly = TRUE) &&
    requireNamespace("htmlwidgets", quietly = TRUE)) {
  format_game_id <- function(game_id) {
    parts <- str_split(game_id, "\\*", simplify = TRUE)
    rows  <- as.integer(as.numeric(parts[, 1]))
    cols  <- as.integer(as.numeric(parts[, 2]))
    paste0(rows, " x ", cols, " ", parts[, 3])
  }

  boot_r2 <- bootstrap_r2_resample(model_base_quad, novice_df, n_boot = 1000)
  boot_preds <- bootstrap_prediction_ci(formula(model_base_quad), novice_df)

  df_interactive <- novice_df %>%
    mutate(predicted = predict(model_base_quad)) %>%
    left_join(boot_preds, by = "game_id") %>%
    mutate(
      game_name  = format_game_id(game_id),
      hover_text = paste0(
        "<b>Game:</b> ", game_name, "<br>",
        "<b>Human Mean:</b> ", round(humans_mean, 1), "<br>",
        "<b>Model Prediction:</b> ", round(predicted, 1)
      )
    )

  p_interactive <- ggplot(df_interactive,
                          aes(x = predicted, y = humans_mean, text = hover_text)) +
    geom_point(size = 3, alpha = 0.8, color = "red") +
    geom_errorbar(aes(ymin = ymin, ymax = ymax),
                  width = 0.1, size = 1.1, alpha = 0.8, color = "red") +
    geom_errorbarh(aes(xmin = pred_lower, xmax = pred_upper),
                   height = 0.1, size = 1.1, alpha = 0.8, color = "red") +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey") +
    theme_classic(base_size = 14) +
    labs(x = "Model Prediction", y = "Human Funness")

  interactive_widget <- plotly::ggplotly(p_interactive, tooltip = "text") %>%
    plotly::layout(hoverlabel = list(bgcolor = "white"))
  out_file <- normalizePath("plots/interactive_funness_plot.html", mustWork = FALSE)
  saved <- tryCatch({
    htmlwidgets::saveWidget(interactive_widget, file = out_file, selfcontained = TRUE)
    TRUE
  }, error = function(e) {
    htmlwidgets::saveWidget(interactive_widget, file = out_file, selfcontained = FALSE)
    FALSE
  })
  cat(sprintf("[interactive] plots/interactive_funness_plot.html  (R² = %.2f%s)\n",
              boot_r2["mean"],
              if (!saved) "  -- non-self-contained, see _files/" else ""))
}

# Export scatter data
export_scatter_data(novice_df, model = NULL, x_col = "emd_unscaled",
                    path = "fig_data_files/fig4_just_emd_scatter.csv")
export_scatter_data(novice_df, model = NULL, x_col = "challenge_unscaled",
                    path = "fig_data_files/fig4_just_challenge_scatter.csv")
export_scatter_data(novice_df, model = NULL, x_col = "len_unscaled",
                    path = "fig_data_files/fig4_just_len_scatter.csv")
export_scatter_data(novice_df, model = model_base_lin,
                    path = "fig_data_files/fig4_model_base_lin_scatter.csv")
export_scatter_data(novice_df, model = model_base_quad,
                    path = "fig_data_files/fig4_model_base_quad_scatter.csv")


# --- adding extra features on top of the quadratic base -------------------
backtick_traits <- sprintf("`%s`", GAME_TRAITS)
aug_models <- list(
  `board-size`           = lm(update(FORMULA_BASE_QUAD, . ~ . + board_size),           data = novice_df),
  `num-constraints`      = lm(update(FORMULA_BASE_QUAD, . ~ . + num_constraints),      data = novice_df),
  `special-trait-counts` = lm(update(FORMULA_BASE_QUAD, . ~ . + special_trait_counts), data = novice_df),
  `all-binary-traits`    = lm(as.formula(paste0(
    "humans_mean ~ emd + challenge + poly(len, 2, raw = TRUE) + ",
    paste(backtick_traits, collapse = " + ")
  )), data = novice_df)
)

cat("\nAdding extra features on top of the quadratic base:\n")
cat(make_anova_comparison_table(
  base_model = model_base_quad,
  alt_models = aug_models,
  labels     = names(aug_models),
  col_label  = "Added Feature",
  caption    = "ANOVA: adding additional features"
))

# Trait-counts effect plot
just_trait_counts <- lm(humans_mean ~ poly(special_trait_counts, 2, raw = TRUE),
                        data = novice_df)
p_trait <- ggplot(novice_df, aes(x = special_trait_counts, y = humans_mean)) +
  geom_point(size = 3, alpha = 0.7) +
  geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.3, size = 1.1, alpha = 0.2) +
  stat_smooth(method = "lm", formula = y ~ poly(x, 2, raw = TRUE),
              se = TRUE, color = "darkgreen") +
  theme_classic(base_size = 16) +
  labs(x = "Trait Counts", y = "Human Fun") +
  annotate("text", x = Inf, y = Inf,
           label = sprintf("R² = %.2f", summary(just_trait_counts)$r.squared),
           hjust = 1.1, vjust = 1.5, size = 8, fontface = "bold")
ggsave("plots/special-trait-counts-effect.png", p_trait,
       width = 6, height = 5, dpi = 300)


quad_fit <- fit_funness_model(novice_df, FORMULA_BASE_QUAD, n_boot = 1000)

write_coefs_latex(
  quad_fit$coefs,
  path    = "tables/intuitive_gamer_quad_baseline_summary_full.tex",
  caption = "Intuitive Gamer Quadratic Baseline: Bootstrapped Mean and 95\\% CI (Full Data)",
  label   = "tab:intuitive_gamer_quad_baseline_summary_full"
)
write_csv(quad_fit$coefs, "tables/intuitive_gamer_quad_baseline_summary_full.csv")

cat("\nIntuitive Gamer quadratic baseline:\n")
summary_funness_fit(quad_fit)


# --- binary-traits-only model ----------------------------------------
binary_formula <- as.formula(paste0(
  "humans_mean ~ ", paste(backtick_traits, collapse = " + ")
))
binary_fit <- fit_funness_model(novice_df, binary_formula, n_boot = 1000)

violin_df <- binary_fit$coef_samples %>%
  pivot_longer(everything(), names_to = "Parameter", values_to = "Estimate") %>%
  filter(Parameter != "(Intercept)") %>%
  mutate(Pretty = factor(GAME_TRAITS_PRETTY[Parameter], levels = GAME_TRAITS_PRETTY)) %>%
  group_by(Pretty) %>%
  mutate(Lower = quantile(Estimate, 0.025, na.rm = TRUE),
         Upper = quantile(Estimate, 0.975, na.rm = TRUE),
         Mean  = mean(Estimate, na.rm = TRUE)) %>%
  ungroup()

p_violin <- ggplot(violin_df, aes(x = Pretty, y = Estimate, fill = Pretty)) +
  geom_violin(alpha = 0.7, color = "black") +
  geom_point(aes(y = Mean), color = "black", size = 2) +
  geom_errorbar(aes(ymin = Lower, ymax = Upper), width = 0.2, color = "black") +
  coord_flip() +
  theme_minimal(base_size = 14) +
  guides(fill = "none") +
  labs(title = "Bootstrapped Coefficients: Binary Game Traits (Funness)",
       x = "Game Trait", y = "Coefficient Estimate")
ggsave("plots/funness_models/binary_traits_violin.png", p_violin,
       width = 8, height = 5, dpi = 300)

plot_predicted_vs_human(
  novice_df, binary_fit$model,
  point_color = "orange",
  output_path = "plots/funness_models/binary_traits_scatter.png"
)
