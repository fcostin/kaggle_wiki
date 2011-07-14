# first attempt at fitting logistic regression model
# to distinguish between test & training populations
# based solely on input features, in order to
# approximately correct for covariate shift.
#
# follows blog post by alex smola:
#	http://blog.smola.org/post/4110255196/real-simple-covariate-shift-correction


library(glmnet)

parse_args <- function() {
	argv <- commandArgs(trailingOnly = TRUE)
	if (length(argv) != 3) {
		stop("usage: training_data.csv test_inputs.csv out_importance_weights.csv\n")
	}
	res <- list()
	res[['training_data_file_name']] <- argv[[1]]
	res[['test_inputs_file_name']] <- argv[[2]]
	res[['weights_file_name']] <- argv[[3]]
	return(res)
}

dbg_save_cv_plot <- function(fit, plot_file_name) {
	cat(sprintf('saving CV curve to "%s"\n', cv_file_name))
	pdf(cv_file_name)
	plot(fit)
	dev.off()
}

save_importance_weights <- function(weights, file_name) {
	cat(sprintf('saving cov shift training importance weights to "%s"\n', file_name))
	colnames(weights)[1] <- 'weights'
	write.table(weights, file_name, sep = ',')
}

estimate_cov_shift_training_weights <- function(args) {
	cat(sprintf('reading training data from "%s"\n', args[['training_data_file_name']]))
	d_train <- read.table(args[['training_data_file_name']], header = TRUE, sep = ',')
	n_usrs <- nrow(d_train)
	n_inputs <- ncol(d_train) - 1
	# drop actual target feature
	d_train <- d_train[, 1:n_inputs]
	d_train[['class']] <- -1 # tag to signify training population
	cat(sprintf("n_usrs : %d, n_inputs : %d\n", n_usrs, n_inputs))

	cat(sprintf('reading test inputs from "%s"\n', args[['test_inputs_file_name']]))
	d_test <- read.table(args[['test_inputs_file_name']], header = TRUE, sep = ',')
	# no actual target feature known for these ones
	d_test <- d_test[, 1:n_inputs]
	# tag 1 to signify test population
	d_test[['class']] <- 1 # tag to signify test population
	
	cat(sprintf('merging tagged train and test populations\n'))
	d_merged <- rbind(d_train, d_test)
	x <- data.matrix(d_merged[, 1:n_inputs])
	y <- as.factor(d_merged[, n_inputs + 1])
	# alpha is elastic net param. alpha = 1 is L1 regularisation
	cat(sprintf('fitting logistic regression model using cv.glmnet\n'))
	fit <- cv.glmnet(
		x,
		y,
		family = 'binomial',
		alpha = 1, # elastic net interp param
		nlambda = 20, # how many regularisation weights to try?
		nfolds = 10,
		type.measure = 'class' # loss for CV - set it to something i can interpret
	)
	cat(sprintf('glmnet chose cross-validated lambda = %f\n', fit$lambda.1se))
	cat(sprintf('predicting on training examples to estimate importance weights\n'))
	z <- predict(fit, x[1:n_usrs, ])
	importance_weights <- exp(z)
	cat(sprintf('ok\n'))
	return(importance_weights)
}

main <- function() {
	args <- parse_args()
	weights <- estimate_cov_shift_training_weights(args)
	save_importance_weights(weights, args[['weights_file_name']])
}

main()
