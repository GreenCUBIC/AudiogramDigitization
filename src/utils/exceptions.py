#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

class InsufficientLabelsException(Exception):
    def __init__(self):
        self.message = f"An insufficient number of labels was detected."
        self.code = "INSUFFICIENT_LABELS"

class InsufficientLinesException(Exception):
    def __init__(self):
        self.message = f"An insufficient number of lines was detected."
        self.code = "INSUFFICIENT_LINES"

class UndefinedPTAException(Exception):
    def __init__(self):
        self.message = f"Something prevented the calculation of a pure tone average. Verify that all the thresholds are available."
        self.code = "UNDEFINED_PTA_EXCEPTION"

class MixedEarsException(Exception):
    def __init__(self, feature: str):
        self.message = f"You attempted to compute the {feature} of the audiogram, but provided thresholds coming from both ears. Ensure that only thresholds from one ear are provided with the ThresholdSet."
        self.code = "MIXED_EARS_EXCEPTION"
