from __future__ import annotations

import json
import math
from datetime import datetime
from typing import Iterable, Tuple

from sqlmodel import select

from ..db import session_scope
from ..models import CurveModel, KeywordVolume
from ..providers.naver import NaverSearchProvider


class CurveService:
    def __init__(self) -> None:
        self.naver = NaverSearchProvider()

    def refresh_and_predict(
        self, keywords: Iterable[str] | None = None, force_refresh: bool = False
    ) -> Tuple[CurveModel, dict, dict[str, int | str]]:
        keywords = list(keywords or [])
        with session_scope() as session:
            model = session.exec(select(CurveModel).order_by(CurveModel.updated_at.desc())).first()
            if not model or force_refresh:
                params = self._train_parameters(session)
                payload = json.dumps(params)
                if not model:
                    model = CurveModel(params_json=payload)
                    session.add(model)
                    session.flush()
                else:
                    model.params_json = payload
                    model.updated_at = datetime.utcnow()
                    session.add(model)
                    session.flush()
            params = json.loads(model.params_json)
            predictions: dict[str, int | str] = {}
            for keyword in keywords:
                volume_info = self.naver.monthly_search_volume(keyword)
                rank = self._predict_rank(volume_info["total"], params)
                predictions[keyword] = rank
        return model, params, predictions

    def _train_parameters(self, session) -> dict:
        volumes = [kv.volume_total for kv in session.exec(select(KeywordVolume)).all()]
        if not volumes:
            pivot = 5000
            steepness = 0.0015
            scale = 900
        else:
            pivot = sum(volumes) / len(volumes)
            steepness = 0.002
            scale = 800
        return {"pivot": pivot, "steepness": steepness, "scale": scale}

    def _predict_rank(self, volume: int, params: dict) -> int | str:
        scale = params.get("scale", 800)
        steepness = params.get("steepness", 0.0015)
        pivot = params.get("pivot", 5000)
        exponent = -steepness * (volume - pivot)
        rank = 1 + int(scale / (1 + math.exp(exponent)))
        if rank > 1000:
            return "1000+"
        return max(1, rank)


__all__ = ["CurveService"]
