from analysis import load_classifier, package_classifier, POSITIVE, NEUTRAL, NEGATIVE

classifier = load_classifier()
package_classifier({"classifier": classifier,
                    "pos_cutoff": 0.84,
                    "neg_cutoff": 0.66,
                    "pos_label": POSITIVE,
                    "neut_label": NEUTRAL,
                    "neg_label": NEGATIVE,
                    "pos_recall": 0.462963,
                    "pos_precision": 0.793651,
                    "neg_recall": 0.653333,
                    "neg_precision": 0.790323,
                   })
