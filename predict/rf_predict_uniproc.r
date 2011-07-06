library(randomForest)

print('reading the data')
d <- read.table('usr_edits_per_5month.csv', header = TRUE, sep = ',')
n_usrs <- nrow(d)
n_months <- ncol(d)
print(sprintf("n_usrs : %d, n_months : %d", n_usrs, n_months))

thin_frac = 1.0
print(sprintf("thinning rows down to %.3f", thin_frac))
indices = 1:n_usrs
thindices = sample(indices, round(thin_frac * n_usrs))
d_raw <- d
d <- log(1.0 + d_raw[thindices, ])
n_thinned_usrs <- nrow(d)

TARGET_WINDOW <- 1

print('making thinned training set')
train_input_col_lo <- 1
train_input_col_hi <- n_months - (2 * TARGET_WINDOW)
train_output_col_lo <- n_months - (2 * TARGET_WINDOW) + 1
train_output_col_hi <- n_months - TARGET_WINDOW
x_train <- d[, train_input_col_lo:train_input_col_hi]
if (train_output_col_hi > train_output_col_lo) {
	y_train <- apply(d[, train_output_col_lo:train_output_col_hi], 1, sum)
} else {
	y_train <- d[, train_output_col_lo]
}

print('making thinned test set')
test_input_col_lo <- 1 + TARGET_WINDOW
test_input_col_hi <- n_months - TARGET_WINDOW
test_output_col_lo <- n_months - TARGET_WINDOW + 1
test_output_col_hi <- n_months
x_test <- d[, test_input_col_lo:test_input_col_hi]
if (test_output_col_hi > test_output_col_lo) {
	y_test <- apply(d[, test_output_col_lo:test_output_col_hi], 1, sum)
} else {
	y_test <- d[, test_output_col_lo]
}


# hack : set same col names so R isnt confused
colnames(x_test) <- colnames(x_train)
colnames(y_test) <- colnames(y_test)

print('training random forest')
rf <- randomForest(
	x_train,
	y_train,
	ntree = 50,
	do.trace = 10,
	importance = FALSE
)

y_train_pred <- predict(rf, x_train)
r_train <- (sum((y_train - y_train_pred) ** 2) / n_thinned_usrs) ** 0.5
print(sprintf('error on thinned training set: %.3f', r_train))

y_test_pred <- predict(rf, x_test)
r_test <- (sum((y_test - y_train_pred) ** 2) / n_thinned_usrs) ** 0.5
print(sprintf('error on thinned test set: %.3f', r_test))

print('making full training set')
d <- log(1.0 + d_raw)
train_input_col_lo <- 1
train_input_col_hi <- n_months - 2
train_output_col <- n_months - 1
x_train <- d[, train_input_col_lo:train_input_col_hi]
y_train <- d[, train_output_col]

print('making full test set')
test_input_col_lo <- 2
test_input_col_hi <- n_months - 1
test_output_col <- n_months
x_test <- d[, test_input_col_lo:test_input_col_hi]
y_test <- d[, test_output_col]
# hack : set same col names so R isnt confused
colnames(x_test) <- colnames(x_train)
colnames(y_test) <- colnames(y_test)

y_train_pred <- predict(rf, x_train)
r_train <- (sum((y_train - y_train_pred) ** 2) / n_thinned_usrs) ** 0.5
print(sprintf('error on full training set: %.3f', r_train))

y_test_pred <- predict(rf, x_test)
r_test <- (sum((y_test - y_train_pred) ** 2) / n_thinned_usrs) ** 0.5
print(sprintf('error on full test set: %.3f', r_test))



print('making full production training set')
d <- log(1.0 + d_raw)
train_input_col_lo <- 1
train_input_col_hi <- n_months - 1
train_output_col <- n_months
x_train <- d[, train_input_col_lo:train_input_col_hi]
y_train <- d[, train_output_col]

print('making full production test inputs (n.b. no outputs known)')
test_input_col_lo <- 2
test_input_col_hi <- n_months
x_test <- d[, test_input_col_lo:test_input_col_hi]
# hack : set same col names so R isnt confused
colnames(x_test) <- colnames(x_train)

print('retraining model on production training data')
rf <- randomForest(
	x_train,
	y_train,
	ntree = 50,
	do.trace = 10,
	importance = FALSE
)

y_train_pred <- predict(rf, x_train)
r_train <- (sum((y_train - y_train_pred) ** 2) / n_thinned_usrs) ** 0.5
print(sprintf('error on full production training set: %.3f', r_train))

print('making prediction on production inputs, saving to disk')
df_predictions <- data.frame(y = predict(rf, x_test))
rownames(df_predictions) <- rownames(d_raw)
write.table(df_predictions, 'predictions.csv', sep = ',')
print('fin.')
