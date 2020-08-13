# Copyright 2020 Cortex Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Any

import os
import threading as td


class ModelsTree:
    """
    A class to hold models in memory.

    For a model to be removed from memory, it must not hold any references to the model outside this class.
    """

    def __init__(self):
        self._models = {}
        self._locks = {}

    def has_model(self, model: str, version: str) -> bool:
        return self.get_model(model, version) is not None

    def get_model(self, name: str, version: str) -> Any:
        model_id = f"{name}-{version}"
        try:
            self._locks[model_id].acquire()
        except:
            self._locks[model_id].release()
            return None
        model = self._models[model_id]
        self._locks[model_id].release()

        return model

    def remove_model(self, name: str, version: str) -> None:
        model_id = f"{name}-{version}"
        try:
            self._locks[model_id].acquire()
        except:
            self._locks[model_id].release()
            return
        del self._models[model_id]
        self._locks[model_id].release()

    def load_model(self, model: Any, name: str, version: str) -> None:
        model_id = f"{name}-{version}"
        try:
            self._locks[model_id].acquire()
        except:
            lock = td.Lock()
            lock_id = id(lock)
            self._locks[model_id] = lock
            self._locks[model_id].acquire()
            if id(self._locks[model_id]) is not lock_id:
                self._locks[model_id].release()
                raise RuntimeException("caught lock generated by another thread; retry")

        self._models[model_id] = model
        self._locks[model_id].release()

    def get_model_names(self) -> List[str]:
        model_names = [model_name.split("-") for model_name in self._models.keys()]
        return list(set(model_names))

    def get_model_versions(self, model_name) -> List[str]:
        return [model.split("-")[1] for model in models if model.startswith(model_name)]
