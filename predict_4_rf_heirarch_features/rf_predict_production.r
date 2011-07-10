library(randomForest)
library(foreach)
library(doMC)
registerDoMC()

TRAIN_DATA_FILE_NAME <- 'features_depth_2_8/data_set_shift_0.csv'
PRODUCTION_DATA_FILE_NAME <- 'features_depth_2_8/data_set_production_inputs.csv'

print('reading training data')
d_train <- read.table(TRAIN_DATA_FILE_NAME, header = TRUE, sep = ',')
print('reading production input data (n.b. no response col)')
d_production <- read.table(PRODUCTION_DATA_FILE_NAME, header = TRUE, sep = ',')
n_usrs <- nrow(d_train)
n_inputs <- ncol(d_train) - 1
print(sprintf("n_usrs : %d, n_inputs : %d", n_usrs, n_inputs))

# preprocess all input & output cols (of counts) with phi transform
phi <- function(x) {
	log(1.0 + x)
}

d_train <- phi(d_train)
d_production <- phi(d_production)

n_procs <- 2
n_trees <- 150
print(sprintf('training random forest: %d trees over %d procs', n_trees, n_procs))
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
print(sprintf('error on training set: %.3f', r_train))

print('predicting on production input data')
df_production_pred <- data.frame(y = predict(rf, d_production))
rownames(df_production_pred) <- rownames(d_production)
print('saving to "predictions.csv"')
write.table(df_production_pred, 'predictions.csv', sep = ',')
print('fin.')
