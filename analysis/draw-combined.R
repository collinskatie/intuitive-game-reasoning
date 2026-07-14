# ----------
# analysis code for draw request models
# note: some help from Claude on R code

# --- Libraries -------------------------------------------------------------
library(tidyverse)     
library(arrow)        
library(jsonlite)     
library(broom)       
library(kableExtra)    

set.seed(123)

setwd("~/intuitive-game-reasoning/analysis")

# --- Helper ----------------------------------------------------------------
compute_utility <- function(draw_prob, win_prob) {
  win_prob - (1 - win_prob - draw_prob)
}

get_variant_df_list <- function(dir_path) {
  variant_dirs <- list.dirs(dir_path, recursive = FALSE)
  setNames(
    lapply(variant_dirs, function(path) {
      list.files(path, pattern = "\\.feather$", full.names = TRUE) |>
        lapply(read_feather)
    }),
    basename(variant_dirs)
  )
}

# --- Data ------------------------------------------------------------------

variant_dirs  <- list.dirs("variant2dfs_feather", recursive = FALSE)
variant2dfs   <- setNames(
  lapply(variant_dirs, function(path) {
    list.files(path, pattern = "\\.feather$", full.names = TRUE) |>
      lapply(read_feather)
  }),
  basename(variant_dirs)
)

# --- Results containers ----------------------------------------------------
fit_results   <- list()        # store every bootstrap’s coefficients
plots_dir     <- "contour_avg"
dir.create(plots_dir, showWarnings = FALSE)
fig_data_dir  <- "fig_data_files"
dir.create(fig_data_dir, showWarnings = FALSE)


# Load human funness data 
novice_fun_components_df <- read_csv("../model-data/local_model_readout_fun_features.csv")
game2think_fun <- setNames(
  lapply(novice_fun_components_df$humans, fromJSON),
  novice_fun_components_df$game_id
)

# --- Per-variant loop ------------------------------------------------------
for (variant in names(variant2dfs)) {
  
  raw_dfs <- variant2dfs[[variant]]
  
  # ----------- Process bootstraps ---------------
  # Est exp value rel to player who received draw request
  # As we model their decision of whether to accept/reject
  processed_dfs <- lapply(seq_along(raw_dfs), function(i) {
    raw_dfs[[i]] |>
      filter(accept_reject %in% c("accept", "reject")) |>
      mutate(
        utility     = 0.5 * compute_utility(all_draw, received_player_win), # bonus of $0.5 for every game win
        game_length = exp_rem_len_mean,
        accept      = as.integer(accept_reject == "accept")
      ) |>
      rowwise() |>
      mutate(fun_think = mean(game2think_fun[[as.character(game)]], na.rm = TRUE)) |>
      ungroup() |>
      filter(
        !is.na(utility), !is.na(game_length), !is.na(fun_think),
        game_length >= 0, fun_think >= 0
      ) |>
      mutate(row_id = row_number()) # key so rows match across bootstraps
  })
  
  models <- lapply(processed_dfs, \(df)
                   glm(accept ~ utility + game_length + fun_think,
                       data = df, family = binomial())
  )
  
  # Transforming exp value with utility and exp length remaining 
  for (i in seq_along(processed_dfs)) {
    coefs <- coef(models[[i]])
    β_u   <- coefs["utility"]
    β_len <- coefs["game_length"]
    
    if (is.na(β_u) || is.na(β_len) || abs(β_u) < 1e-10) next  
    
    β_3   <- ifelse(abs(β_u) > 1e-10, -β_len / β_u, 0)
    
    processed_dfs[[i]] <- processed_dfs[[i]] |>
      mutate(EV = utility - β_3 * game_length,
             replicate = i)
  }
  
  # ----------- Collate for summaries ------------------------
  pooled_df <- bind_rows(processed_dfs)
  
  df_summ <- pooled_df |>
    group_by(row_id) |>
    summarise(
      EV_mu  = mean(EV),
      EV_lo  = quantile(EV, .025),
      EV_hi  = quantile(EV, .975),
      
      fun_mu = mean(fun_think),
      fun_lo = quantile(fun_think, .025),
      fun_hi = quantile(fun_think, .975),
      
      accept = first(accept),
      .groups = "drop"
    )
  
  # ----------- Prediction grid ------------------------------
  EV_range  <- seq(min(df_summ$EV_mu), max(df_summ$EV_mu), length.out = 100)
  print(EV_range)
  fun_range <- seq(min(pooled_df$fun_think), max(pooled_df$fun_think), length.out = 100)
  grid      <- expand_grid(EV = EV_range, fun_think = fun_range)
  
  # ----------- Ensemble prediction on grid ------------------
  pred_mat <- sapply(seq_along(models), function(i) {
    coefs <- coef(models[[i]])
    plogis(
      coefs["(Intercept)"] +
        coefs["utility"] * grid$EV +          # ← β_u · EV
        coefs["fun_think"] * grid$fun_think   # ← β_fun · fun
    )
  })
  grid$prob <- rowMeans(pred_mat)
  
  # Helper: Extract legend from a ggplot
  extract_legend <- function(p) {
    gtable <- ggplotGrob(p)
    legend <- gtable$grobs[which(sapply(gtable$grobs, function(x) x$name) == "guide-box")][[1]]
    ggplotify::as.ggplot(legend)
  }
  
  # Base plot (with legend for extraction)
  plot_with_legend <- ggplot() +
    geom_tile(data = grid,
              aes(x = EV, y = fun_think, fill = prob), alpha = 0.30) +
    geom_contour(data = grid,
                 aes(x = EV, y = fun_think, z = prob),
                 breaks = 0.5, colour = "black", size = 1) +
    geom_point(data = df_summ,
               aes(x = EV_mu, y = fun_mu, colour = factor(accept)),
               size = 3, alpha = 0.85) +
    scale_fill_gradient2("Avg  P(Accept)",
                         low = "orange1", mid = "white", high = "springgreen4",
                         midpoint = 0.5, limits = c(0, 1)) +
    scale_colour_manual("Decision",
                        values = c("1" = "springgreen4", "0" = "orange1"),
                        labels = c("Reject Draw", "Accept Draw")) +
    labs(x = "", y = "") +
    theme_minimal() +
    theme(
      legend.text = element_text(size = 20),
      legend.title = element_text(size = 24, face = "bold"),
      legend.key.size = unit(1.2, "cm"),
      legend.spacing.y = unit(0.4, 'cm')
    )
  
  # Extract and save legend
  legend_grob <- extract_legend(plot_with_legend)
  
  legend_grob <- legend_grob +
    theme(
      plot.margin = margin(20, 10, 10, 10, unit = "pt"),       # top increased
      legend.margin = margin(t = 12, r = 6, b = 4, l = 6, unit = "pt")
    )
  
  # Convert grob to a real ggplot so ggsave respects full layout
  legend_plot <- ggplotify::as.ggplot(legend_grob)
  
  # Save with enough height
  ggsave(file.path(plots_dir, paste0("legend_", variant, ".svg")),
         legend_plot, width = 4, height = 6.5, dpi = 300)
  
  # Main plot without legend
  plot_2d <- plot_with_legend + theme(legend.position = "none")
  
  # Save plot without legend
  ggsave(file.path(plots_dir, paste0("contour_", variant, "_avg.svg")),
         plot_2d, width = 8, height = 6, dpi = 300)
  
  # Save figure data to CSV
  # Grid data for contour/heatmap
  write_csv(grid, file.path(fig_data_dir, paste0("draw_fig_", variant, "_grid.csv")))
  # Point data (summarized observations)
  write_csv(df_summ, file.path(fig_data_dir, paste0("draw_fig_", variant, "_points.csv")))
  
  # ----------- Store coefficients for later summary ---------
  fit_results <- append(fit_results,
                        purrr::imap(models, function(mdl, i) {
                          tibble(
                            variant       = variant,
                            bootstrap     = i,
                            intercept     = coef(mdl)[["(Intercept)"]],
                            beta_utility  = coef(mdl)[["utility"]],
                            beta_length   = coef(mdl)[["game_length"]],
                            beta_fun      = coef(mdl)[["fun_think"]],
                            llik          = logLik(mdl)[[1]] / nobs(mdl)
                          )
                        })
  )
}

# --- Summarise coefficients across bootstraps ------------------------------
all_coefs <- bind_rows(fit_results)

coef_summary <- all_coefs |>
  group_by(variant) |>
  summarise(
    avg_intercept  = mean(intercept),
    lo95_intercept = quantile(intercept, .025),
    hi95_intercept = quantile(intercept, .975),
    
    avg_utility    = mean(beta_utility),
    lo95_utility   = quantile(beta_utility, .025),
    hi95_utility   = quantile(beta_utility, .975),
    
    avg_length     = mean(beta_length),
    lo95_length    = quantile(beta_length, .025),
    hi95_length    = quantile(beta_length, .975),
    
    avg_fun        = mean(beta_fun),
    lo95_fun       = quantile(beta_fun, .025),
    hi95_fun       = quantile(beta_fun, .975),
    
    avg_ll         = mean(llik),
    lo95_ll        = quantile(llik, .025),
    hi95_ll        = quantile(llik, .975),
    .groups = "drop"
  )

variant2viz <- c(full        = "Intuitive Gamer",
                 expert      = "Expert",
                 rand        = "Random",
                 `abl-block` = "Only Offense",
                 `abl-connect` = "Only Defense")

coef_table <- coef_summary |>
  filter(variant %in% names(variant2viz)) |>
  mutate(
    Variant      = variant2viz[variant],
    Intercept    = sprintf("%.2f (%.2f, %.2f)", avg_intercept, lo95_intercept, hi95_intercept),
    Utility      = sprintf("%.2f (%.2f, %.2f)", avg_utility,   lo95_utility,   hi95_utility),
    Game_Length  = sprintf("%.3f (%.3f, %.3f)", avg_length,    lo95_length,    hi95_length),
    Fun_Think    = sprintf("%.4f (%.4f, %.4f)", avg_fun,       lo95_fun,       hi95_fun),
    Log_Lik      = sprintf("%.2f (%.2f, %.2f)", avg_ll,        lo95_ll,        hi95_ll)
  ) |>
  select(Variant, Log_Lik, Utility, Game_Length, Fun_Think)

coef_table |>
  kable(format = "latex",
        booktabs = TRUE,
        caption  = "Mean coefficients (95\\% CIs) by variant",
        label    = "tab:coef_summary") |>
  kable_styling(latex_options = c("HOLD_position"))