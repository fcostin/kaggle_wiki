library(randomForest)
library(foreach)
library(doMC)
registerDoMC()

parse_args <- function() {
	argv <- commandArgs(trailingOnly = TRUE)
	if (length(argv) != 4) {
		stop("usage: n_procs n_trees training_data.csv forest.rdata\n")
	}
	res <- list()
	res[['n_procs']] <- as.integer(argv[[1]])
	res[['n_trees']] <- as.integer(argv[[2]])
	res[['training_data_file_name']] <- argv[[3]]
	res[['out_file_name']] <- argv[[4]]
	return(res)
}


phi <- function(x) {
	log(1.0 + x)
}

train_rf <- function(forest_args) {
	cat(sprintf('reading training data from "%s"\n', forest_args[['training_data_file_name']]))
	d_train <- read.table(forest_args[['training_data_file_name']], header = TRUE, sep = ',')
	n_usrs <- nrow(d_train)
	n_inputs <- ncol(d_train) - 1
	print(sprintf("n_usrs : %d, n_inputs : %d", n_usrs, n_inputs))
	
	# preprocess response col (of counts) with phi transform
	d_train[, ncol(d_train)] <- phi(d_train[, ncol(d_train)])

	n_procs <- forest_args[['n_procs']]
	n_trees <- forest_args[['n_trees']]
	if (n_trees %% n_procs != 0) {
		stop(sprintf('ERROR: n_procs (%d) must divide n_trees (%d).', n_procs, n_trees))
	}
	cat(sprintf('training random forest: %d trees over %d procs\n', n_trees, n_procs))
	rf <- foreach(
		trees_per_proc = rep(n_trees / n_procs, n_procs),
		.combine = combine,
		.packages = 'randomForest'
	) %dopar% {
		randomForest(
			d_train[, 1:n_inputs],
			d_train[, n_inputs + 1],
			ntree = trees_per_proc,
			do.trace = 10,
			importance = FALSE
		)
	}
	y_train_pred <- predict(rf, d_train[, 1:n_inputs])
	r_train <- (sum((d_train[, n_inputs + 1] - y_train_pred) ** 2) / n_usrs) ** 0.5
	cat(sprintf('error on training set: %.3f\n', r_train))
	return(rf)

}

save_forest <- function(rf, out_file_name) {
	cat(sprintf('saving rf model to file "%s"\n', out_file_name))
	save('rf', file = out_file_name, compress = TRUE)
}

main <- function() {
	args <- parse_args()
	rf <- train_rf(args)
	save_forest(rf, args[['out_file_name']])
}

main()
