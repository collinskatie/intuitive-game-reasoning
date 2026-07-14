# ==============================================================================
# Refits the funness regression on participants' post-play ratings

# Help from Claude Code for refactor
# ==============================================================================
setwd("~/intuitive-game-reasoning/analysis/funness/")
source("setup_helpers.R")

for (d in c("plots", "tables")) if (!dir.exists(d)) dir.create(d, recursive = TRUE)


# --- Load just-think (all 121; but filter infinite) + post-play (subset of 41) ----------------------
types     <- read_json(META_FILES$game2game_type)
stimuli   <- read_json(META_FILES$game_stimuli)
novice_df <- prepare_funness_data(FEATURE_FILES$Novice, types, stimuli)

play_human_fun <- fromJSON(POST_PLAY_FILE)
play_df <- tibble(game_id = names(play_human_fun),
                  ratings = unname(play_human_fun)) %>%
  mutate(
    ci_vals           = map(ratings, bootstrap_mean_ci),
    new_humans_parsed = ratings,
    new_human_mean    = map_dbl(ci_vals, "mean"),
    new_human_lower   = map_dbl(ci_vals, "lower"),
    new_human_upper   = map_dbl(ci_vals, "upper")
  ) %>%
  select(-ci_vals, -ratings)

# Replace the human columns with post-play values; keep simulation features.
postplay_df <- novice_df %>%
  inner_join(play_df, by = "game_id") %>%
  mutate(humans_parsed = new_humans_parsed,
         humans_mean   = new_human_mean,
         ymin          = new_human_lower,
         ymax          = new_human_upper) %>%
  select(-starts_with("new_"))

cat(sprintf("Matched %d games between just-think and post-play.\n", nrow(postplay_df)))


run_basic_analysis <- function(df, label_suffix, output_dir = "plots") {
  base_lin  <- lm(FORMULA_BASE_LIN,  data = df)
  base_quad <- lm(FORMULA_BASE_QUAD, data = df)

  just_emd       <- lm(humans_mean ~ emd,       data = df)
  just_challenge <- lm(humans_mean ~ challenge, data = df)
  just_len       <- lm(humans_mean ~ poly(len, 2, raw = TRUE), data = df)

  drops <- list(
    emd       = lm(humans_mean ~ challenge + len, data = df),
    challenge = lm(humans_mean ~ emd + len,       data = df),
    len       = lm(humans_mean ~ emd + challenge, data = df)
  )
  cat(sprintf("\n[%s] Linear ablations:\n", label_suffix))
  cat(make_anova_comparison_table(
    base_lin, drops, c("emd", "challenge", "len"),
    col_label = "Feature Removed",
    caption   = paste0("ANOVA: linear ablations (", label_suffix, ")")
  ))

  quad_alts <- list(
    emd       = lm(humans_mean ~ poly(emd, 2, raw = TRUE) + challenge + len, data = df),
    challenge = lm(humans_mean ~ emd + poly(challenge, 2, raw = TRUE) + len, data = df),
    len       = lm(humans_mean ~ emd + challenge + poly(len, 2, raw = TRUE), data = df)
  )
  cat(sprintf("\n[%s] Linear vs quadratic:\n", label_suffix))
  cat(make_anova_comparison_table(
    base_lin, quad_alts, c("emd", "challenge", "len"),
    col_label = "Predictor",
    caption   = paste0("ANOVA: linear vs quadratic (", label_suffix, ")")
  ))

  # Scatter plots
  out_path <- function(stub) file.path(output_dir, paste0(stub, "-", label_suffix, ".png"))
  plot_simple_predictor(df, just_emd,       "emd_unscaled",       "Balance",
                        quadratic = FALSE, output_path = out_path("just-emd"))
  plot_simple_predictor(df, just_challenge, "challenge_unscaled", "Challenge",
                        quadratic = FALSE, output_path = out_path("just-challenge"))
  plot_simple_predictor(df, just_len,       "len_unscaled",       "Game Length",
                        quadratic = TRUE,  output_path = out_path("just-len"))
  plot_predicted_vs_human(df, base_lin,  output_path = out_path("model-base-lin"))
  plot_predicted_vs_human(df, base_quad, output_path = out_path("model-base-quad"))

  invisible(list(base_lin = base_lin, base_quad = base_quad))
}


# --- Run on post-play --------------------------------------------------------
postplay_models <- run_basic_analysis(postplay_df, label_suffix = "ppt")


# --- Adding extra features (post-play) ---------------------------------------
backtick_traits <- sprintf("`%s`", GAME_TRAITS)
aug_models_pp <- list(
  `board-size`           = lm(update(FORMULA_BASE_QUAD, . ~ . + board_size),           data = postplay_df),
  `num-constraints`      = lm(update(FORMULA_BASE_QUAD, . ~ . + num_constraints),      data = postplay_df),
  `special-trait-counts` = lm(update(FORMULA_BASE_QUAD, . ~ . + special_trait_counts), data = postplay_df),
  `all-binary-traits`    = lm(as.formula(paste0(
    "humans_mean ~ emd + challenge + poly(len, 2, raw = TRUE) + ",
    paste(backtick_traits, collapse = " + ")
  )), data = postplay_df)
)

cat("\n[post-play] Adding extra features:\n")
cat(make_anova_comparison_table(
  base_model = postplay_models$base_quad,
  alt_models = aug_models_pp,
  labels     = names(aug_models_pp),
  col_label  = "Added Feature",
  caption    = "ANOVA: adding additional features (post-play)"
))


# --- Just-think (matched 41) vs Post-play: coefficient comparison ------------
think_matched_df <- novice_df %>% filter(game_id %in% postplay_df$game_id)

think_fit_matched <- fit_funness_model(think_matched_df, FORMULA_BASE_QUAD, n_boot = 1000)
postplay_fit      <- fit_funness_model(postplay_df,      FORMULA_BASE_QUAD, n_boot = 1000)

write_coefs_latex(
  think_fit_matched$coefs,
  path    = "tables/quad_baseline_think_matched.tex",
  caption = "Quadratic Baseline (Just-Think, 41 games matched to post-play)",
  label   = "tab:quad_baseline_think_matched"
)
write_coefs_latex(
  postplay_fit$coefs,
  path    = "tables/quad_baseline_postplay.tex",
  caption = "Quadratic Baseline (Post-Play)",
  label   = "tab:quad_baseline_postplay"
)


# --- Density plot of bootstrapped coefficients -------------------------------
combined_samples <- bind_rows(
  think_fit_matched$coef_samples %>% mutate(Set = "Just-Think"),
  postplay_fit$coef_samples      %>% mutate(Set = "Post-Play")
) %>%
  pivot_longer(cols = -Set, names_to = "Parameter", values_to = "Estimate") %>%
  mutate(Parameter = rename_param(Parameter))

p_density <- ggplot(combined_samples, aes(x = Estimate, fill = Set, colour = Set)) +
  geom_density(alpha = 0.35, adjust = 1.25) +
  facet_wrap(~ Parameter, scales = "free", ncol = 2) +
  theme_classic(base_size = 15) +
  labs(title = "Bootstrapped Parameter Distributions:\nMatched Just-Think vs Post-Play",
       x = "Parameter Value", y = "Density") +
  scale_fill_manual(values   = c("Just-Think" = "purple", "Post-Play" = "grey")) +
  scale_colour_manual(values = c("Just-Think" = "purple", "Post-Play" = "grey"))

ggsave("plots/param_comparison_think_matched_vs_postplay.png", p_density,
       width = 9, height = 7, dpi = 300)


# --- Summary printout --------------------------------------------------------
cat("\n--- Just-think (matched 41) ---\n")
summary_funness_fit(think_fit_matched)

cat("\n--- Post-play ---\n")
summary_funness_fit(postplay_fit)
