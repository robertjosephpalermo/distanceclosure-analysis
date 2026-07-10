from dataclasses import dataclass
from enum import StrEnum

class Algorithm(StrEnum):
    HEURISTIC = "heuristic"
    ITERATIVE = "iterative"
    FLAGGED = "flagged"
    CLOSURE = "closure"
    HEURISTIC_APPROX = "heuristic_approximation"


class Metric(StrEnum):
    METRIC = "metric"
    ULTRAMETRIC = "ultrametric"


class DataColumn(StrEnum):
    TYPE = "type"
    RELATIVE_PATH = "relative_path"
    NODES = "nodes"
    EDGES = "edges"
    DENSITY = "density"
    CV = "cv"
    HEURISTIC_METRIC_DT = Algorithm.HEURISTIC + "_" + Metric.METRIC + "_dt"
    ITERATIVE_METRIC_DT = Algorithm.ITERATIVE + "_" + Metric.METRIC + "_dt"
    FLAGGED_METRIC_DT = Algorithm.FLAGGED + "_" + Metric.METRIC + "_dt"
    CLOSURE_METRIC_DT = Algorithm.CLOSURE + "_" + Metric.METRIC + "_dt"
    HEURISTIC_APPROX_METRIC_DT = Algorithm.HEURISTIC_APPROX + "_" + Metric.METRIC + "_dt"
    HEURISTIC_ULTRAMETRIC_DT = Algorithm.HEURISTIC + "_" + Metric.ULTRAMETRIC + "_dt"
    ITERATIVE_ULTRAMETRIC_DT = Algorithm.ITERATIVE + "_" + Metric.ULTRAMETRIC + "_dt"
    FLAGGED_ULTRAMETRIC_DT = Algorithm.FLAGGED + "_" + Metric.ULTRAMETRIC + "_dt"
    CLOSURE_ULTRAMETRIC_DT = Algorithm.CLOSURE + "_" + Metric.ULTRAMETRIC + "_dt"
    HEURISTIC_APPROX_ULTRAMETRIC_DT = Algorithm.HEURISTIC_APPROX + "_" + Metric.ULTRAMETRIC + "_dt"
    

class Alternative(StrEnum):
    LESS = "less"
    GREATER = "greater"
    TWO_SIDED = "two-sided"


@dataclass(frozen=True)
class AlgorithmMetadata:
    color: str
    metric_dt: DataColumn
    ultrametric_dt: DataColumn 

    def get_runtime_column(self, metric: Metric) -> str:
        if metric == Metric.METRIC:
            return self.metric_dt
        elif metric == Metric.ULTRAMETRIC:
            return self.ultrametric_dt
        else:
            raise ValueError(f"Unknown metric: {metric}")
       
        
ALGORITHM_METADATA = {
    Algorithm.HEURISTIC: AlgorithmMetadata(
        color="red",
        metric_dt=DataColumn.HEURISTIC_METRIC_DT,
        ultrametric_dt=DataColumn.HEURISTIC_ULTRAMETRIC_DT
    ),
    Algorithm.ITERATIVE: AlgorithmMetadata(
        color="orange",
        metric_dt=DataColumn.ITERATIVE_METRIC_DT,
        ultrametric_dt=DataColumn.ITERATIVE_ULTRAMETRIC_DT
    ),
    Algorithm.FLAGGED: AlgorithmMetadata(
        color="blue",
        metric_dt=DataColumn.FLAGGED_METRIC_DT,
        ultrametric_dt=DataColumn.FLAGGED_ULTRAMETRIC_DT
    ),
    Algorithm.CLOSURE: AlgorithmMetadata (
        color="purple",
        metric_dt=DataColumn.CLOSURE_METRIC_DT,
        ultrametric_dt=DataColumn.CLOSURE_ULTRAMETRIC_DT
    )
}

