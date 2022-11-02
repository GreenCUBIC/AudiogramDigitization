# Audiology Report Digitizer

## Authors:

- *Francois Charih* (Team Leader) - francoischarih@sce.carleton.ca - Carleton University
- *James R. Green* (Principal Investigator) - jrgreen@sce.carleton.ca - Carleton University

## Summary

This software, developed in collaboration with the [Workplace Safety and
Insurance Board](https://www.wsib.ca/en), was designed to facilitate the
digitization of audiology reports, in particular the audiograms contained
therein.

This repository contains the source code for:

1. **Audiogram digitization algorithm**: a set of Python scripts that implement
the digitization algorithm using deep convolutional neural networks.

2. **Audiology report annotation interface**: An electron-based desktop
application that allows for the rapid annotation of audiograms contained within
audiology reports. These annotations can be used to train deep convolutional
neural networks to detect the elements that make up the audiogram, and that are
needed for the computer to comprehend the audiogram.

- Demo: https://huggingface.co/spaces/weiren119/AudiogramDigitization
## Audiogram digitization algorithm

We recommend using Python 3.9 to run the algorithm as this is the version that we
tested.

Before using any of this software, you must install the dependencies in a virtual environment
and activate that virtual environment.

To set up the virtual environment:

```
$ python3 -m venv environment
$ source environment/bin/activate
$ pip3 install -r requirements.txt
```

This will create the virtual environment in the directory `environment`. This only
needs to be done once. (If you are warned that the versions of torch or torchvision are not
available, then, perhaps you are not using Python 3.9.)

Then, to run any command, you must ensure that this environment is activated
by running (on macOS/Linux):

```
$ source environment/bin/activate
```

or on Windows

```
C:\> environment\Scripts\activate.bat
```

⚠️⚠️⚠️⚠️⚠️⚠️
**Important:** You will need to fix a bug in the torch library by changing `F.hardswish(input, self.inplace)` to `F.hardswish(input)` in `environment/lib/python3.9/site-packages/torch/nn/modules/activation.py`.
⚠️⚠️⚠️⚠️⚠️⚠️
## Running the digitizer (in the console)

To run the digitizer, do:

```
$ ./src/digitize_report.py -i <path to image or directory with images> -o <directory where the resulting JSON document should be saved>
```

The resulting JSON files have the same basename as the input image,
but with the `.json` extension.

The JSON files output by the algorithm are a simple list of threshold objects that look as follows:

```
[
    {
        "ear": "left",
        "conduction": "air",
        "masking": false,
        "measurementType": "AIR_UNMASKED_LEFT",
        "frequency": 6000,
        "threshold": 60,
        "response": true
    },
    {
        "ear": "left",
        "conduction": "air",
        "masking": false,
        "measurementType": "AIR_UNMASKED_LEFT",
        "frequency": 3000,
        "threshold": 60,
        "response": true
    },
    ...
]
```

You can visually inspect the digitized audiogram as a PNG image by running the script `plot_audiogram.py`:

```
$ ./src/plot_audiogram.py -i <path_to_digitized_audiogram_json> -o <path to output image>
```

## (Re-)training the object detection models

The models used in this algorithm are all
[YoloV5](https://github.com/ultralytics/yolov5) models. There is an [excellent
tutorial](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data) on how
to train a YOLOv5 model on custom data. You may download and use the annotation
application to collect annotations in JSON format and use these annotations to
(re)-train the object detectors.

**Note that you will need to convert the locations of the objects in the JSON
annotation file to the YOLO format. This is well described in the tutorial.**

Once the models are trained, you can simply drop the weights (`best.pt`) in the appropriate
location, i.e. in `models/<audiograms|symbols|labels>/latest/weights`, depending on whether
it is the model trained to detect audiograms, symbols or axis labels.