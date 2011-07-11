# Pipeline for training a random forest from 5 month count data
# and predicting counts for submission to kaggle.
#
# Produces the result "predictions.csv"

INPUT_DATA_FILE = "data/edits_5month.csv"

# Split input data into training and test data files
# (expressed as two tasks, if one of these is run then
# both outputs will be generated)
file "gen/training.csv" => [INPUT_DATA_FILE, "split_ts_data.r"] do
	sh "Rscript split_ts_data.r #{INPUT_DATA_FILE} gen/training.csv gen/test_inputs.csv"
end
file "test_inputs.csv" => [INPUT_DATA_FILE, "split_ts_data.r"] do
	sh "Rscript split_ts_data.r #{INPUT_DATA_FILE} gen/training.csv gen/test_inputs.csv"
end

# Train random forest (using multiple cores), then save
# random forest representation to disk. This part is the
# most time intensive.
file "gen/forest.rdata" => ["rf_train.r", "gen/training.csv"] do
	n_procs = 2 # how many cores do we have to play with?
	n_trees = 50 # how many trees do we want in total
	if n_trees % n_procs != 0
		abort("n_procs (#{n_procs}) does not divide n_trees (#{n_trees})")
	end
	sh "Rscript rf_train.r #{n_procs} #{n_trees} gen/training.csv gen/forest.rdata"
end

# Load random forests from disk, use them to make predictions on test input data
file "gen/raw_predictions.csv" => ["rf_predict.r", "gen/forest.rdata", "gen/test_inputs.csv"] do
	sh "Rscript rf_predict.r gen/forest.rdata gen/test_inputs.csv gen/raw_predictions.csv"
end

# Format the raw predictions to properly match the format expected by kaggle
# (i.e. proper user ids in first col, rows sorted wrt user ids, header)
file "gen/predictions.csv" => ["fmt_predictions.py", "gen/raw_predictions.csv"] do
	sh "python fmt_predictions.py gen/raw_predictions.csv gen/predictions.csv"
end

task :default => "gen/predictions.csv"