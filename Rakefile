# Pipeline for training a random forest from 5 month count data
# and predicting counts for submission to kaggle.
#
# Produces the result "gen/predictions.csv"

INPUT_WEEKLY_COUNTS = "data/usr_edits_per_week.npy"
INPUT_WEEKLY_ABS_DELTA = "data/usr_abs_delta_per_week.npy"

# Split input data into training and test data files
# (expressed as two tasks, if one of these is run then
# both outputs will be generated)
file "gen/training.csv" => [INPUT_WEEKLY_COUNTS, INPUT_WEEKLY_ABS_DELTA, "make_features.py"] do
	cmd = [
		"python make_features.py",
		INPUT_WEEKLY_COUNTS,
		INPUT_WEEKLY_ABS_DELTA,
		"gen/training.csv",
		"gen/test_inputs.csv",
	]
	sh cmd.join(" ")
end

file "gen/test_inputs.csv" => [INPUT_WEEKLY_COUNTS, INPUT_WEEKLY_ABS_DELTA, "make_features.py"] do
	cmd = [
		"python make_features.py",
		INPUT_WEEKLY_COUNTS,
		INPUT_WEEKLY_ABS_DELTA,
		"gen/training.csv",
		"gen/test_inputs.csv",
	]
	sh cmd.join(" ")
end

# Train random forest (using multiple cores), then save
# random forest representation to disk. This part is the
# most time intensive.
file "gen/forest.rdata" => ["rf_train.r", "gen/training.csv"] do
	n_procs = 2 # how many cores do we have to play with?
	n_trees = 1200 # how many trees do we want in total
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

task :clean do
	sh "rm -fv gen/*.csv"
	sh "rm -fv gen/forest.rdata"
end

task :default => "gen/predictions.csv"
