library(glmnet)

phi <- function(x) {
	log(x + 1.0)
}

phi_inv <- function(x) {
	exp(x) - 1.0
}

parse_args <- function() {
	argv <- commandArgs(trailingOnly = TRUE)
	if (length(argv) != 3) {
		stop("usage: glmnet.rdata inputs.csv predictions.csv\n")
	}
	res <- list()
	res[['glmnet_file_name']] <- argv[[1]]
	res[['inputs_file_name']] <- argv[[2]]
	res[['predictions_file_name']] <- argv[[3]]
	return(res)
}

load_inputs <- function(inputs_file_name) {
	cat(sprintf('reading input data from "%s"\n', inputs_file_name))
	d_inputs <- read.table(inputs_file_name, header = TRUE, sep = ',')
	n_usrs <- nrow(d_inputs)
	n_inputs <- ncol(d_inputs) 
	cat(sprintf("n_usrs : %d, n_inputs : %d\n", n_usrs, n_inputs))
	return(d_inputs)
}

load_glmnet <- function(file_name) {
	cat(sprintf('loading glmnet model from file "%s"\n', file_name))
	# n.b. load into specified environment (R pollutes global
	# environment by default mumble grumble)
	env <- environment()
	load(file_name, env)
	coeffs <- env[['glmnet_coeffs']]
	return(coeffs)
}

compute_predictions <- function(glm_coeffs, inputs) {
	# tranform all inputs with phi
	# (this has to match pre-processing performed by train)
	inputs <- phi(inputs)
	print('computing predictions')
	glm_coeffs <- as.numeric(glm_coeffs)
	intercept <- glm_coeffs[1]
	print(intercept)
	beta <- glm_coeffs[2:length(glm_coeffs)]
	print(beta)
	y <- intercept
	for(i in 1:ncol(inputs)) {
		y <- y + beta[i] * inputs[, i]
	}
	print('transforming predictions')
	return(phi_inv(pmax(y, 0.0)))
}

save_predictions <- function(predictions, row_names, file_name) {
	cat(sprintf('saving predictions to "%s"\n', file_name))
	df <- data.frame(y = predictions)
	rownames(df) <- row_names
	write.table(df, file_name, sep = ',')
}

main <- function() {
	args <- parse_args()
	inputs <- load_inputs(args[['inputs_file_name']])
	glm_fit <- load_glmnet(args[['glmnet_file_name']])
	predictions <- compute_predictions(glm_fit, inputs)
	save_predictions(predictions, row.names(inputs), args[['predictions_file_name']])
}

main()
