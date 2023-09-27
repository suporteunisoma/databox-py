import mlflow
import os
import pandas as pd
import uuid
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

def start_mlflow(experiment_name):
    mlflow_track_uri = os.getenv("MLFLOW_TRACKING_URI")
    if mlflow_track_uri is None or mlflow_track_uri == "":
        mlflow_track_uri = "http://192.168.7.234:5000/"

    client_obj = MlflowClient(tracking_uri=mlflow_track_uri)

    exp = client_obj.get_experiment_by_name(experiment_name)
    if exp is None:
        exp_id = client_obj.create_experiment(name=experiment_name)
    else:
        exp_id = exp.experiment_id

    run_obj = mlflow.start_run(experiment_id=exp_id)
    return run_obj

def save_artifact(run_obj, df_artifact=None, file_path_artifact=None):
    mlflow_track_uri = os.getenv("MLFLOW_TRACKING_URI")
    if mlflow_track_uri is None or mlflow_track_uri == "":
        os.environ["MLFLOW_TRACKING_URI"] = "http://192.168.7.234:5000/"

    if file_path_artifact is not None:
        mlflow.log_artifact(file_path_artifact, run_id=run_obj.info.run_id)

    if df_artifact is not None:
        uuid_str = str(uuid.uuid1())
        df_path = f"/tmp/{uuid_str}.csv"
        df_artifact.to_csv(df_path, index=False)
        mlflow.log_artifact(df_path, run_id=run_obj.info.run_id)
        os.remove(df_path)

def finish_mlflow(run_obj, df_parameter=None, df_metric=None, final_status):
    mlflow_track_uri = os.getenv("MLFLOW_TRACKING_URI")
    if mlflow_track_uri is None or mlflow_track_uri == "":
        mlflow_track_uri = "http://192.168.7.234:5000/"

    client_obj = MlflowClient(tracking_uri=mlflow_track_uri)

    if df_parameter is not None:
        for _, row in df_parameter.iterrows():
            mlflow.log_param(row["params"], row["values"], run_id=run_obj.info.run_id)

    if df_metric is not None:
        for _, row in df_metric.iterrows():
            mlflow.log_metric(row["params"], row["values"], run_id=run_obj.info.run_id)

    mlflow.end_run(status=final_status, run_id=run_obj.info.run_id)

def check_experiment(experiment_name, client):
    exper_list = client.list_experiments(view_type=ViewType.ALL)

    exp_id = 0
    for exp in exper_list:
        if exp.name == experiment_name:
            exp_id = exp.experiment_id
            if exp.lifecycle_stage == "deleted":
                client.restore_experiment(exp_id)

    return exp_id

class MLFlowStatusEnum:
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    KILLED = "KILLED"
