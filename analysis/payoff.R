# Code for assessing non-sim-based payoff (fitting to some games)
# note: help from Claude on R code

require(mgcv)
require(caret)
require(ggplot2)
require(tidyr)
require(dplyr)
library(xtable)


require(ISLR)
library(tidyverse)

library(jsonlite)
library(dplyr)   

think_res <- jsonlite::fromJSON(
  "final_processed_res/think/human_processed.json",
  flatten = TRUE
)

# payoff 
# think_res$human_payoff$`1.0*10.0*3 pieces in a row wins.`$payoff

# Define game-level binary trait names (must match the order used in get_game_characteristics)
game_characteristics <- c(
  "larger_than_3x3_board",
  "diff3inrow",
  "non_square_board",
  "asymmetric_win",
  "asymmetric_play",
  "constrained_win",
  "misere"
)


game2game_type <- fromJSON("game_info/game2game_type.json")  # Example list, should be populated with game data
game2idx <- fromJSON("game_info/game2idx.json")        # Example list, should be populated with game data
game_stimuli <- fromJSON("game_info/game_stimuli.json")    # Example list, should be populated with game stimuli data

compute_board_size <- function(game_id) {
  if (!(game_id %in% names(game2game_type))) return(NA)
  game_obj <- game_stimuli[[game_id]]
  game_obj[['board-x']] * game_obj[['board-y']]
}

compute_win_cond <- function(game_id) {
  if (!(game_id %in% names(game2game_type))) return(NA)
  game_obj <- game_stimuli[[game_id]]
  game_obj[['N']]
}

get_game_characteristics <- function(game_id) {
  if (!(game_id %in% names(game2game_type))) {
    return(list(game_traits = rep(NA, length(game_characteristics)), 
                special_trait_counts = NA, 
                num_constraints = NA))
  }
  
  game_type <- game2game_type[[game_id]]
  game_obj <- game_stimuli[[game_id]]
  board_size <- game_obj[['board-x']] * game_obj[['board-y']]
  K <- game_obj[['N']]
  
  num_constraints <- 0
  game_traits <- rep(0, length(game_characteristics))
  
  game_traits[1] <- as.numeric(board_size > 9)  # larger_than_3x3_board
  game_traits[2] <- as.numeric(K != 3)            # diff3inrow
  game_traits[3] <- as.numeric(game_type == 'rectangle-board')
  game_traits[4] <- as.numeric(game_type %in% c('player1-constraintA', 'player1-constraintB', 'diff-win'))
  game_traits[5] <- as.numeric(game_type %in% c('player1-2pieces', 'player2-2pieces'))
  game_traits[6] <- as.numeric(game_type %in% c('only-diag', 'no-diag', 'player1-constraintB', 'player1-constraintA'))
  game_traits[7] <- as.numeric(game_type == 'loss')
  
  if (game_traits[4] == 1) num_constraints <- num_constraints + 1
  if (game_type %in% c('only-diag', 'no-diag')) num_constraints <- num_constraints + 1
  
  special_trait_counts <- sum(game_traits)
  list(game_traits = game_traits, special_trait_counts = special_trait_counts, num_constraints = num_constraints)
}

add_game_features <- function(df) {
  if (!"game_id" %in% colnames(df)) {
    for (trait in c("board_size", "win_condition", "special_trait_counts", "num_constraints", game_characteristics)) {
      df[[trait]] <- NA
    }
    return(df)
  }
  
  df$board_size <- sapply(df$game_id, compute_board_size)
  df$win_condition <- sapply(df$game_id, compute_win_cond)
  
  traits <- lapply(df$game_id, get_game_characteristics)
  df$special_trait_counts <- sapply(traits, function(x) x$special_trait_counts)
  df$num_constraints <- sapply(traits, function(x) x$num_constraints)
  
  for (i in seq_along(game_characteristics)) {
    df[[game_characteristics[i]]] <- sapply(traits, function(x) x$game_traits[i])
  }
  return(df)
}


bootstrap_ci <- function(x) {
  q <- quantile(x, c(0.025, 0.975))
  c(lower = q[1], upper = q[2])
}

plot_payoff_model <- function(model, model_name, df, output_dir = "plots/payoff_models") {
  if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)
  
  # Bootstrap R²
  B <- 1000
  preds <- predict(model)
  actuals <- df$humans_mean
  humans_per_game <- lapply(df$game_id, function(id) think_res$human_payoff[[id]]$payoff)
  
  r2_boot <- replicate(B, {
    boot_means <- sapply(humans_per_game, function(x) {
      x <- x[!is.na(x)]
      if (length(x) == 0) return(NA)
      mean(sample(x, replace = TRUE))
    })
    cor(preds, boot_means, use = "complete.obs")^2
  })
  r2_boot <- r2_boot[!is.na(r2_boot)]
  r2_label <- sprintf("R² = %.2f (%.2f, %.2f)",
                      mean(r2_boot),
                      quantile(r2_boot, 0.025),
                      quantile(r2_boot, 0.975))
  
  # Bootstrap model prediction CIs
  boot_pred_mat <- replicate(B, {
    boot_means <- sapply(humans_per_game, function(x) {
      x <- x[!is.na(x)]
      if (length(x) == 0) return(NA)
      mean(sample(x, replace = TRUE))
    })
    boot_df <- df
    boot_df$humans_mean <- boot_means
    fit <- tryCatch(lm(formula(model), data = boot_df), error = function(e) NULL)
    if (!is.null(fit)) predict(fit, newdata = df) else rep(NA, nrow(df))
  })
  
  pred_ci_df <- t(apply(boot_pred_mat, 1, function(x) quantile(x, c(0.025, 0.975), na.rm = TRUE)))
  colnames(pred_ci_df) <- c("xmin", "xmax")
  
  # Final plot data
  df_plot <- df %>%
    mutate(Predicted = preds,
           ymin = sapply(humans_per_game, function(x) quantile(x, 0.025, na.rm = TRUE)),
           ymax = sapply(humans_per_game, function(x) quantile(x, 0.975, na.rm = TRUE)),
           xmin = pred_ci_df[, "xmin"],
           xmax = pred_ci_df[, "xmax"])
  
  # Plot
  p <- ggplot(df_plot, aes(x = Predicted, y = humans_mean)) +
    geom_point(size = 3, alpha = 0.8, color="orange") +
    geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.2, alpha = 0.2,color = "orange") +
    geom_errorbarh(aes(xmin = xmin, xmax = xmax), height = 0.2, alpha = 0.2,color = "orange") +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "orange") +
    theme_classic(base_size = 16) +
    labs(
      title = r2_label,
      x = "Model", y = "Human"
    ) +
    theme(plot.title = element_text(hjust = 0.5, size = 18, face = "bold"))
  
  fname <- paste0(output_dir, "/", gsub("[^a-zA-Z0-9]", "_", tolower(model_name)), ".png")
  ggsave(fname, p, width = 6, height = 5, dpi = 300)
  
  return(p)
}


analyze_payoff_df <- function(payoff_data, label) {
  cat("\nAnalyzing:", label, "\n")
  
  human_vals <- think_res$human_payoff 
  humans_mean <- sapply(human_vals, mean)
  
  # payoff df -- make
  
  #payoff_df <- add_game_features(payoff_df)
  # Construct payoff_df with one row per game
  game_ids <- names(think_res$human_payoff)
  
  # Compute mean payoff per game
  payoff_df <- tibble(
    game_id = game_ids,
    humans_mean = sapply(game_ids, function(id) {
      mean(think_res$human_payoff[[id]]$payoff, na.rm = TRUE)
    })
  )
  
  # Add game features
  payoff_df <- add_game_features(payoff_df)
  
  
  
  numeric_features <- c("board_size", "special_trait_counts")
  game_trait_features <- game_characteristics
  
  for (f in numeric_features) {
    if (f %in% colnames(payoff_df)) payoff_df[[f]] <- scale(payoff_df[[f]])
  }
  
  
  models <- list(
    "Linear Game Features" = humans_mean ~ special_trait_counts + win_condition,
    "Linear All Game Traits" = humans_mean ~
      `larger_than_3x3_board` + `diff3inrow` + `non_square_board` +
      `asymmetric_win` + `asymmetric_play` + `constrained_win` + `misere` +
      board_size + win_condition + special_trait_counts,
    "Linear Only Game Traits" = humans_mean ~
      `larger_than_3x3_board` + `diff3inrow` + `non_square_board` +
      `asymmetric_win` + `asymmetric_play` + `constrained_win` + `misere`
  )
  
  
  # if (all(is.na(payoff_df$board_size))) {
  #   models <- models[grep("Baseline", names(models))]
  #   warning("No game data available. Using only baseline models.")
  # }
  # 
  set.seed(123)
  B <- 1000
  boot_results <- list()
  
  perform_bootstrap <- function(formula, model_type) {
    r2_vals <- numeric(B)
    
    for (b in 1:B) {
      idx <- sample(1:nrow(payoff_df))
      split <- floor(nrow(payoff_df) / 2)
      train <- payoff_df[idx[1:split], ]
      test <- payoff_df[idx[(split + 1):length(idx)], ]
      
      formula_vars <- all.vars(formula)
      train <- train[complete.cases(train[, formula_vars]), ]
      test <- test[complete.cases(test[, formula_vars]), ]
      
      if (nrow(train) == 0 || nrow(test) == 0) {
        r2_vals[b] <- NA
        next
      }
      
      model <- tryCatch(
        if (grepl("GAM", model_type)) gam(formula, data = train) else lm(formula, data = train),
        error = function(e) NULL
      )
      
      if (is.null(model)) {
        r2_vals[b] <- NA
        next
      }
      
      preds <- predict(model, newdata = test)
      actuals <- test$humans_mean
      r2_vals[b] <- cor(preds, actuals, use = "complete.obs")^2
    }
    return(r2_vals)
  }
  
  for (model_name in names(models)) {
    cat("Bootstrapping:", model_name, "\n")
    boot_results[[model_name]] <- perform_bootstrap(models[[model_name]], model_name)
  }
  
  ci_bounds <- lapply(boot_results, function(x) bootstrap_ci(x[!is.na(x)]))
  boot_summary <- data.frame(
    Model = names(boot_results),
    Mean_R2 = sapply(boot_results, function(x) mean(x, na.rm = TRUE)),
    CI_Lower = sapply(ci_bounds, function(x) x[1]),
    CI_Upper = sapply(ci_bounds, function(x) x[2]),
    N_Valid = sapply(boot_results, function(x) sum(!is.na(x))),
    Dataset = label
  )
  
  print(boot_summary[order(-boot_summary$Mean_R2), ])
  
  cat("\n--- Final Model Coefficients & Prediction Plots ---\n")
  
  for (model_name in names(models)) {
    formula <- models[[model_name]]
    model_type <- if (grepl("GAM", model_name)) "gam" else "lm"
    cat("\nModel:", model_name, "\n")
    
    model <- tryCatch(
      if (model_type == "gam") gam(formula, data = payoff_df) else lm(formula, data = payoff_df),
      error = function(e) NULL
    )
    
    if (is.null(model)) {
      cat("Model fitting failed.\n")
      next
    }
    
    # Summary output
    print(summary(model))
    
    # Coefficient plot for linear models
    if (model_type == "lm") {
      coefs <- broom::tidy(model)
      p_coef <- ggplot(coefs, aes(x = reorder(term, estimate), y = estimate)) +
        geom_point() +
        geom_errorbar(aes(ymin = estimate - std.error, ymax = estimate + std.error), width = 0.2) +
        coord_flip() +
        theme_minimal() +
        labs(title = paste("Coefficient Estimates:", model_name),
             x = "Predictor", y = "Estimate ± SE")
      print(p_coef)
    }
    
    # GAM smooth plots
    if (model_type == "gam") {
      par(mfrow = c(1, 1))  # Reset just in case
      plot(model, residuals = TRUE, pch = 16, pages = 1)
    }
    
    # Predicted vs actual
    preds <- predict(model, newdata = payoff_df)
    actuals <- payoff_df$humans_mean
    
    p <- ggplot(data.frame(Predicted = preds, Actual = actuals), aes(x = Predicted, y = Actual)) +
      geom_point(alpha = 0.6) +
      geom_abline(slope = 1, intercept = 0, linetype = "dashed") +
      coord_cartesian(xlim = c(-1.05, 1.05), ylim = c(-1.05, 1.05)) +
      theme_minimal() +
      labs(title = "",
           x = "Model",
           y = "Human")
    print(p)
  }
  
  
  
  
  
  
  all_summaries[[label]] <<- boot_summary
  
  
  
  cat("\n--- Final Model Coefficients & Prediction Plots ---\n")
  
  for (model_name in names(models)) {
    formula <- models[[model_name]]
    model_type <- if (grepl("GAM", model_name)) "gam" else "lm"
    cat("\nModel:", model_name, "\n")
    
    model <- tryCatch(
      if (model_type == "gam") gam(formula, data = payoff_df) else lm(formula, data = payoff_df),
      error = function(e) NULL
    )
    
    if (is.null(model)) {
      cat("Model fitting failed.\n")
      next
    }
    
    # Print model summary
    print(summary(model))
    
    # Plot predicted vs. actual
    preds <- predict(model, newdata = payoff_df)
    actuals <- payoff_df$humans_mean
    
    p <- ggplot(data.frame(Predicted = preds, Actual = actuals), aes(x = Predicted, y = Actual)) +
      geom_point(alpha = 0.6) +
      geom_abline(slope = 1, intercept = 0, linetype = "dashed") +
      coord_cartesian(xlim = c(-1.05, 1.05), ylim = c(-1.05, 1.05)) +
      theme_minimal() +
      labs(title = "",
           x = "Model",
           y = "Human")
    print(p)
  
  
  g <- plot_payoff_model(model, model_name, payoff_df)
  print(g)
  bootstrap_model_coefs <- function(model, df, n_boot = 1000) {
    humans_per_game <- lapply(df$game_id, function(id) think_res$human_payoff[[id]]$payoff)
    all_coef_names <- names(coef(model))
    coefs_mat <- replicate(n_boot, {
      boot_means <- sapply(humans_per_game, function(x) {
        x <- x[!is.na(x)]
        if (length(x) == 0) return(NA)
        mean(sample(x, replace = TRUE))
      })
      boot_df <- df
      boot_df$humans_mean <- boot_means
      fit <- tryCatch(lm(formula(model), data = boot_df), error = function(e) NULL)
      res <- rep(NA, length(all_coef_names)); names(res) <- all_coef_names
      if (!is.null(fit)) res[names(coef(fit))] <- coef(fit)
      res
    }, simplify = "matrix")
    as_tibble(t(coefs_mat))
  }
  
  coefs_df <- bootstrap_model_coefs(model, payoff_df)
  ci_tbl <- coefs_df %>%
    pivot_longer(cols = everything(), names_to = "Parameter", values_to = "Estimate") %>%
    group_by(Parameter) %>%
    summarise(
      Mean = mean(Estimate, na.rm = TRUE),
      Lower = quantile(Estimate, 0.025, na.rm = TRUE),
      Upper = quantile(Estimate, 0.975, na.rm = TRUE)
    ) %>%
    mutate(Estimate_CI = sprintf("%.3f (%.3f, %.3f)", Mean, Lower, Upper))
  
  xt <- xtable(
    ci_tbl %>% select(Parameter, Estimate_CI),
    caption = paste("Bootstrapped Parameter Estimates (95% CI):", model_name),
    label = paste0("tab:boot_param_", gsub("[^a-zA-Z0-9]", "_", tolower(model_name)))
  )
  print(xt, include.rownames = FALSE, booktabs = TRUE,
        sanitize.text.function = identity,
        file = paste0("payoff_", gsub("[^a-zA-Z0-9]", "_", tolower(model_name)), "_params.tex"))
  
  
  }
  
  
  # Parameter label mapping
  pretty_names <- c(
    larger_than_3x3_board = "Board > 3x3",
    diff3inrow = "K != 3",
    non_square_board = "Non-square Board",
    asymmetric_win = "Asymmetric Win",
    asymmetric_play = "Asymmetric Play",
    constrained_win = "Constrained Win",
    misere = "Misère"
  )
  
  # Bootstrap coefficients
  model_name <- "Linear Only Game Traits"
  payoff_df <- add_game_features(tibble(
    game_id = names(think_res$human_payoff),
    humans_mean = sapply(names(think_res$human_payoff), function(id) {
      mean(think_res$human_payoff[[id]]$payoff, na.rm = TRUE)
    })
  ))
  model <- lm(humans_mean ~
                `larger_than_3x3_board` + `diff3inrow` + `non_square_board` +
                `asymmetric_win` + `asymmetric_play` + `constrained_win` + `misere`,
              data = payoff_df)
  
  coefs_df <- bootstrap_model_coefs(model, payoff_df)
  
  # Prepare violin plot data with clean names
  violin_df <- coefs_df %>%
    pivot_longer(cols = everything(), names_to = "Parameter", values_to = "Estimate") %>%
    filter(!is.na(Estimate), Parameter != "(Intercept)") %>%
    mutate(Pretty = factor(pretty_names[Parameter], levels = pretty_names)) %>%
    group_by(Pretty) %>%
    mutate(
      Lower = quantile(Estimate, 0.025),
      Upper = quantile(Estimate, 0.975),
      Mean = mean(Estimate)
    )
  
  # Generate subtle color palette
  library(scales)
  color_map <- hue_pal()(length(unique(violin_df$Pretty)))
  names(color_map) <- levels(violin_df$Pretty)
  
  # Plot violin
  p_violin <- ggplot(violin_df, aes(x = Pretty, y = Estimate, fill = Pretty)) +
    geom_violin(alpha = 0.7, color = "black") +
    geom_point(aes(y = Mean), color = "black", size = 2) +
    geom_errorbar(aes(ymin = Lower, ymax = Upper), width = 0.2, color = "black") +
    scale_fill_manual(values = color_map) +
    coord_flip() +
    theme_minimal(base_size = 14) +
    guides(fill = "none") +
    labs(
      title = "Bootstrapped Coefficient Distributions: Linear Only Game Traits",
      x = "Game Trait", y = "Coefficient Estimate"
    )
  
  # Save and print
  ggsave("plots/payoff_models/linear_only_game_traits_violin.png", p_violin, width = 8, height = 5, dpi = 300)
  print(p_violin)
  
  
}

all_summaries <- list()

analyze_payoff_df(think_res, 'Non-Sim')


# Combine summaries
overall_summary <- bind_rows(all_summaries)
overall_summary$Model_Short <- factor(overall_summary$Model, 
                                      levels = c("Linear Game Features", "Linear Only Game Traits", "Linear All Game Traits"),
                                      labels = c("Agg Game Features","Game Traits",  "Agg Features and Traits"))

# Plot R2 summaries
p_bar <- ggplot(overall_summary, aes(x = Model_Short, y = Mean_R2, fill = Dataset)) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(aes(ymin = CI_Lower, ymax = CI_Upper), width = 0.2, position = position_dodge(0.9)) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Model R² Comparison", y = "Mean R²", x = "Model")
print(p_bar)

# ------ 



