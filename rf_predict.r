library(randomForest)

parse_args <- function() {
	argv <- commandArgs(trailingOnly = TRUE)
	if (length(argv) != 3) {
		stop("usage: forest.rdata inputs.csv predictions.csv\n")
	}
	res <- list()
	res[['forest_file_name']] <- argv[[1]]
	res[['inputs_file_name']] <- argv[[2]]
	res[['predictions_file_name']] <- argv[[3]]
	return(res)
}


phi <- function(x) {
	log(1.0 + x)
}

phi_inv <- function(x) {
	exp(x) - 1.0
}

load_inputs <- function(inputs_file_name) {
	cat(sprintf('reading input data from "%s"\n', inputs_file_name))
	d_inputs <- read.table(inputs_file_name, header = TRUE, sep = ',')
	n_usrs <- nrow(d_inputs)
	n_inputs <- ncol(d_inputs) 
	cat(sprintf("n_usrs : %d, n_inputs : %d\n", n_usrs, n_inputs))
	return(d_inputs)
}

load_forest <- function(forest_file_name) {
	cat(sprintf('loading rf model from file "%s"\n', forest_file_name))
	# n.b. load into specified environment (R pollutes global
	# environment by default mumble grumble)
	env <- environment()
	load(forest_file_name, env)
	return(env[['rf']])
}

compute_predictions <- function(rf, inputs) {
	return(phi_inv(predict(rf, phi(inputs))))
}

save_predictions <- function(predictions, row_names, file_name) {
	cat(sprintf('saving predictions to "%s"\n', file_name))
	df <- data.frame(y = predictions)
	rownames(df) <- row_names
	write.table(df, 'predictions.csv', sep = ',')
}

main <- function() {
	args <- parse_args()
	inputs <- load_inputs(args[['inputs_file_name']])
	rf <- load_forest(args[['forest_file_name']])
	predictions <- compute_predictions(rf, inputs)
	save_predictions(predictions, row.names(inputs), args[['predictions_file_name']])
}

main()
