# Pipeline for training a random forest from 5 month count data
# and predicting counts for submission to kaggle.
#
# By default, produces the result "gen/predictions.csv"

# ---------------------------------------------------------------
# TOP LEVEL BUILD COMMANDS

# preprocess data, train model, predict, post-process results
task :default => "gen/predictions.csv"

# compile the pdf documentation using latex
task :doc => "doc/description.pdf"

# delete all generated files, apart from the usr_to_index_map
# and the *.npy count tables
task :clean

# clean_everything also deletes the usr_to_index_map and
# both *.npy count tables, which take a while to rebuild
task :clean_everything
# ---------------------------------------------------------------

ORIGINAL_DATA = "original_data/training.tsv"
USR_TO_INDEX_MAP = "data/usr_to_index_map.pickle"
INPUT_WEEKLY_COUNTS = "data/usr_edits_per_week.npy"
INPUT_WEEKLY_ABS_DELTA = "data/usr_abs_delta_per_week.npy"

file USR_TO_INDEX_MAP => ["make_usr_to_index_map.py", ORIGINAL_DATA] do
	cmd = [
		"python make_usr_to_index_map.py",
		ORIGINAL_DATA,
		USR_TO_INDEX_MAP,
	]
	sh cmd.join(" ")
end

file INPUT_WEEKLY_COUNTS => ["count_edits_per_week.py", USR_TO_INDEX_MAP, ORIGINAL_DATA] do
	cmd = [
		"python count_edits_per_week.py",
		ORIGINAL_DATA,
		USR_TO_INDEX_MAP,
		INPUT_WEEKLY_COUNTS,
	]
	sh cmd.join(" ")
end

file INPUT_WEEKLY_ABS_DELTA => ["count_abs_delta_size_per_week.py", USR_TO_INDEX_MAP, ORIGINAL_DATA] do
	cmd = [
		"python abs_delta_size_per_week.py",
		ORIGINAL_DATA,
		USR_TO_INDEX_MAP,
		INPUT_WEEKLY_ABS_DELTA,
	]
	sh cmd.join(" ")
end

task :clean_inputs do
	sh "rm -f #{USR_TO_INDEX_MAP}"
	sh "rm -f #{INPUT_WEEKLY_COUNTS}"
	sh "rm -f #{INPUT_WEEKLY_ABS_DELTA}"
end

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
	cmd = [
		"Rscript rf_train.r",
		"#{n_procs}",
		"#{n_trees}",
		"gen/training.csv",
		"gen/forest.rdata",
	]
	sh cmd.join(" ")
end

# Load random forests from disk, use them to make predictions on test input data
file "gen/raw_predictions.csv" => ["rf_predict.r", "gen/forest.rdata", "gen/test_inputs.csv"] do
	cmd = [
		"Rscript rf_predict.r",
		"gen/forest.rdata",
		"gen/test_inputs.csv gen/raw_predictions.csv",
	]
	sh cmd.join(" ")
end

# Format the raw predictions to properly match the format expected by kaggle
# (i.e. proper user ids in first col, rows sorted wrt user ids, header)
file "gen/predictions.csv" => ["fmt_predictions.py", USR_TO_INDEX_MAP, "gen/raw_predictions.csv"] do
	cmd = [
		"python fmt_predictions.py",
		USR_TO_INDEX_MAP,
		"gen/raw_predictions.csv",
		"gen/predictions.csv",
	]
	sh cmd.join(" ")
end

task :clean_predict do
	sh "rm -fv gen/*.csv"
	sh "rm -fv gen/forest.rdata"
end

task :clean => :clean_predict


file "doc/description.pdf" => "doc/description.tex" do
	# repeat command twice to ensure references show up ...
	sh "pdflatex --output-directory doc description.tex"
	sh "pdflatex --output-directory doc description.tex"
end

task :clean_doc do
	sh "rm -f doc/description.log"
	sh "rm -f doc/description.out"
	sh "rm -f doc/description.aux"
	sh "rm -f doc/description.pdf"
end

task :clean => :clean_doc

task :clean_everything => [:clean, :clean_inputs]

