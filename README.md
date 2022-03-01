# Audiology Report Digitizer

## Authors:

- *Francois Charih* (Team Leader) - francoischarih@sce.carleton.ca - Carleton University
- *James R. Green* (Principal Investigator) - jrgreen@sce.carleton.ca - Carleton University

## Before launching any command

Before using any of this software, you must install the dependencies in a virtual environment
and activate that virtual environment.

To set up the virtual environment:

```
$ python3 -m venv environment
$ source environment/bin/activate
$ pip3 install -r requirements.txt
```

This will create the virtual environment in the directory `environment`. This only
needs to be done once.

Then, to run any command, you must ensure that this environment is activated
by running:

```
$ source environment/bin/activate
```

## Running the digitizer (in the console)

To run the digitizer, do:

```
$ ./src/digitize_report.py -i <path to image or directory with images> -o <directory where the resulting JSON document should be saved>
```

The resulting JSON files have the same basename as the input image,
but with the `.json` extension.

Add the `-a` flag if you want to produce a partial annotation (without corners)
instead of a thresholds list.

## Re-training the models

It may be worth retraining the models periodically as new annotations become
available.

### Collect the data for training

You can put the data in a directory of the form.

```
data
|----images
|------| <put .jpg images here>
|----annotations
|------| <put JSON format annotations here>
```

You will provide the path to this directory when running the training script.

### Training the models

You can easily train the detectors using the `scripts/train_model.py` script (make sure that the
virtual environment is activated). Pass the `-h` flag for instructions.

Running the script will train the detection models and store the resulting
training data (neural network weights) in the directories `models/<audiograms|labels|symbols>/latest`
depending on which detectors are trained.

To revert back to a previous model, you can simply copy the content of the model
to the `models/<audiograms|labels|symbols>/latest` directory:

```
$ rm -rf models/<audiograms|labels|symbols>/latest
$ cp -r models/<audiograms|labels|symbols>/<model_to_restore> models/<audiograms|labels|symbols>/latest
```

**IMPORTANT: IMAGES ARE ASSUMED TO BE IN .jpg format.**
