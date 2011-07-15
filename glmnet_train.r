library(glmnet)

parse_args <- function() {
	argv <- commandArgs(trailingOnly = TRUE)
	if (length(argv) != 3) {
		stop("usage: training_data.csv importance_weights.csv out.rdata\n")
	}
	res <- list()
	res[['training_data_file_name']] <- argv[[1]]
	res[['weights_file_name']] <- argv[[2]]
	res[['out_file_name']] <- argv[[3]]
	return(res)
}

dbg_save_cv_plot <- function(fit, plot_file_name) {
	cat(sprintf('saving CV curve to "%s"\n', plot_file_name))
	pdf(plot_file_name)
	plot(fit)
	dev.off()
}

phi <- function(x) {
	log(1.0 + x)
}

save_glmnet <- function(glmnet, out_file_name) {
	cat(sprintf('saving glmnet model to file "%s"\n', out_file_name))
	# direct save() on glmnet is broken (unsupported i guess)
	# so extract lm coeffs and save those
	glmnet_coeffs <- predict(glmnet, type = "coefficients")
	save('glmnet_coeffs', file = out_file_name, compress = TRUE)
}

fit_glmnet_lasso <- function(args) {
	cat(sprintf('reading training data from "%s"\n', args[['training_data_file_name']]))
	d_train <- read.table(args[['training_data_file_name']], header = TRUE, sep = ',')
	n_usrs <- nrow(d_train)
	n_inputs <- ncol(d_train) - 1
	cat(sprintf("n_usrs : %d, n_inputs : %d\n", n_usrs, n_inputs))

	d_weight <- read.table(args[['weights_file_name']], header = TRUE, sep = ',')
	weights <- as.numeric(d_weight[, ncol(d_weight)])
	
	# hit both inputs & output with phi transform
	# (certainly must be done to output to get
	# error in correct form. looks like it helps
	# doing it to inputs as well (perhaps only
	# helps for subset of cols, but havent looked)

	# n.b. form must be data matrix to feed to glmnet
	d_train <- data.matrix(phi(d_train))
	x <- d_train[, 1:n_inputs]
	y <- d_train[, n_inputs + 1]

	cat(sprintf('fitting regression model using cv.glmnet\n'))
	fit <- cv.glmnet(
		x,
		y,
		weights = weights, # here we go, importance weight
		family = 'gaussian',
		alpha = 0.9, # elastic net interp param
		nlambda = 20, # how many regularisation weights to try?
		nfolds = 10,
		type.measure = 'mse' # loss for CV - set it to something i can interpret
	)
	cat(sprintf('glmnet chose cross-validated lambda = %f\n', fit$lambda.1se))
	print(fit$lambda)
	print(fit$cvm)
	cat(sprintf('predicting on training examples to estimate importance weights\n'))
	dbg_save_cv_plot(fit, 'gen/glmment_predict_dbg_plot.pdf')
	return(fit)
}

main <- function() {
	args <- parse_args()
	fit <- fit_glmnet_lasso(args)
	save_glmnet(fit, args[['out_file_name']])
}

main()
