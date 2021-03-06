import logging
import numpy as np
from edgetpu.detection.engine import BasicEngine

LOGGER = logging.getLogger(__name__)


class DeeplabDetection(object):
    def __init__(self, model, labels, threshold, camera_res):
        self.threshold = threshold
        self.engine = BasicEngine(model)
        self.labels = self.read_labels(labels)
        self.camera_res = camera_res

    def read_labels(self, file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
        labels = {}
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            labels[int(pair[0])] = pair[1].strip()
        return labels

    def pre_process(self, frame):
        frame_expanded = np.expand_dims(frame.get(), axis=0)
        return frame_expanded.flatten()

    def post_process(self, objects):
        processed_objects = []
        for obj in objects:
            # Calculate coordinates in the original image
            obj.bounding_box = obj.bounding_box * self.camera_res
            processed_objects.append(
                {
                    "label": str(self.labels[obj.label_id]),
                    "confidence": round(float(obj.score), 3),
                    "height": round(
                        int(obj.bounding_box[1][1] - obj.bounding_box[0][1]), 3
                    ),
                    "width": round(
                        int(obj.bounding_box[1][0] - obj.bounding_box[0][0]), 3
                    ),
                    "x1": round(int(obj.bounding_box[0][0]), 3),
                    "y1": round(int(obj.bounding_box[0][1]), 3),
                    "x2": round(int(obj.bounding_box[1][0]), 3),
                    "y2": round(int(obj.bounding_box[1][1]), 3),
                }
            )
        return processed_objects

    def return_objects(self, frame):
        tensor = self.pre_process(frame)

        inference_time, results = self.engine.RunInference(tensor)
        # for item in results:
        #    if item > 0:
        #        LOGGER.info(item)
        return results

        # objects = self.post_process(detected_objects)
        # LOGGER.info(self.engine.get_inference_time())
        # return objects
