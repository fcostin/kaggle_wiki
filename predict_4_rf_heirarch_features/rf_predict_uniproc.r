library(randomForest)

TRAIN_DATA_FILE_NAME <- 'features_depth_2_8/data_set_shift_20.csv'
TEST_DATA_FILE_NAME <- 'features_depth_2_8/data_set_shift_0.csv'
PRODUCTION_DATA_FILE_NAME <- 'features_depth_2_8/data_set_production_inputs.csv'

print('reading training data')
d_train <- read.table(TRAIN_DATA_FILE_NAME, header = TRUE, sep = ',')
print('reading test data')
d_test <- read.table(TEST_DATA_FILE_NAME, header = TRUE, sep = ',')
n_usrs <- nrow(d_train)
n_inputs <- ncol(d_train) - 1
print(sprintf("n_usrs : %d, n_inputs : %d", n_usrs, n_inputs))

# preprocess all input & output cols (of counts) with phi transform
phi <- function(x) {
	log(1.0 + x)
}

d_train <- phi(d_train)
d_test <- phi(d_test)

print('training random forest')
rf <- randomForest(
	d_train[, 1:n_inputs],
	d_train[, n_inputs + 1],
	ntree = 150,
	do.trace = 10,
	importance = FALSE
)

y_train_pred <- predict(rf, d_train[, 1:n_inputs])
r_train <- (sum((d_train[, n_inputs + 1] - y_train_pred) ** 2) / n_usrs) ** 0.5
print(sprintf('error on training set: %.3f', r_train))

y_test_pred <- predict(rf, d_test[, 1:n_inputs])
r_test <- (sum((d_test[, n_inputs + 1] - y_test_pred) ** 2) / n_usrs) ** 0.5
print(sprintf('error on test set: %.3f', r_test))

# OK production dataset prediction data

print('reading production input data (no response available)')
d_production <- read.table(PRODUCTION_DATA_FILE_NAME, header = TRUE, sep = ',')
n_usrs <- nrow(d_production)
n_inputs <- ncol(d_production) # n.b. no -1 here as no response col in data set
print(sprintf("n_usrs : %d, n_inputs : %d", n_usrs, n_inputs))

print('predicting on production input data')
df_production_pred <- data.frame(y = predict(rf, d_production))
rownames(df_production_pred) <- rownames(d_production)
print('saving to "predictions.csv"')
write.table(df_production_pred, 'predictions.csv', sep = ',')
print('fin.')
