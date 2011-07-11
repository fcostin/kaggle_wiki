parse_args <- function() {
	argv <- commandArgs(trailingOnly = TRUE)
	if (length(argv) != 3) {
		stop("usage: data.csv out_training_data.csv out_test_inputs.csv\n")
	}
	res <- list()
	res[['data_file_name']] <- argv[[1]]
	res[['out_training_data_file_name']] <- argv[[2]]
	res[['out_test_inputs_file_name']] <- argv[[3]]
	return(res)
}

main <- function() {
	args <- parse_args()
	data <- read.table(
		args[['data_file_name']],
		header = TRUE,
		sep = ','
	)
	training_data <- data
	test_inputs <- data[, 2:ncol(data)]
	for (i in 1:ncol(data)) {
		if (i < ncol(data)) {
			colnames(training_data)[i] <- sprintf('x_%d', i)
			colnames(test_inputs)[i] <- sprintf('x_%d', i)
		} else {
			colnames(training_data)[i] <- 'y'
		}
	}
	write.table(
		training_data,
		file = args[['out_training_data_file_name']],
		sep = ','
	)
	write.table(
		test_inputs,
		file = args[['out_test_inputs_file_name']],
		sep = ','
	)
}

main()
