import mlflow
import os
import uuid

def start_mlflow(experiment_name):

    mlflow_track_uri = get_mlflow_url()
    mlflow.set_tracking_uri(mlflow_track_uri)
    client_obj = mlflow.tracking.MlflowClient()
    print(mlflow.get_tracking_uri())
    os.environ["MLFLOW_TRACKING_URI"] = mlflow_track_uri

    exp = client_obj.get_experiment_by_name(experiment_name)
    if exp is None:
        exp_id = client_obj.create_experiment(name=experiment_name)
    else:
        exp_id = exp.experiment_id

    run_obj = mlflow.start_run(experiment_id=exp_id)
    
    print("run Forest!!!")

    return run_obj

def save_artifact(run_obj, df_artifact=None, file_path_artifact=None):
    if file_path_artifact is not None:
        print(run_obj.info.run_uuid)
        os.system(f"mlflow artifacts log-artifact --local-file {file_path_artifact} --run-id {run_obj.info.run_uid}")

    if df_artifact is not None:
        uuid_str = str(uuid.uuid1())
        df_path = f"/tmp/{uuid_str}.csv"
        df_artifact.to_csv(df_path, index=False)
        os.system(f"mlflow artifacts log-artifact --local-file {df_path} --run-id {run_obj.info.run_uid}")
        os.remove(df_path)

def finish_mlflow(df_parameter=None, df_metric=None):
    mlflow_track_uri = get_mlflow_url()
    mlflow.set_tracking_uri(mlflow_track_uri)
    print(mlflow.get_tracking_uri())
    run = mlflow.active_run()

    if df_parameter is not None:
        for _, row in df_parameter.iterrows():
            mlflow.log_param(row["params"], row["values"])#, run_id=run.info.run_uuid)

    if df_metric is not None:
        for _, row in df_metric.iterrows():
            mlflow.log_metric(row["params"], row["values"])#, run_id=run.info.run_uuid)

    print(f"run_id: {run.info.run_id}; status: {run.info.status}")

    # End run and get status
    mlflow.end_run()
    run = mlflow.get_run(run.info.run_id)
    print(f"run_id: {run.info.run_id}; status: {run.info.status}")
    print("--")

    # Check for any active runs
    print(f"Active run: {mlflow.active_run()}")


def check_experiment(experiment_name, mlflow_client):
    print(experiment_name)
    exp = mlflow_client.get_experiment_by_name(experiment_name)
    print(exp)

    if exp is None:
        print("Creating a new experiment...")
        exp_id = mlflow_client.create_experiment(name=experiment_name)
        print(exp_id)
    else:
        print("MLFlow experiment already exists..")
        if exp.lifecycle_stage == "deleted":
            print("The experiment exists but cannot be used because it was already deleted")

    return exp

# class MLFlowStatusEnum:
#     FINISHED = "FINISHED"
#     FAILED = "FAILED"
#     KILLED = "KILLED"

def get_mlflow_url():
    uri = os.getenv("MLFLOW_URI")
    if uri == "" or uri is None:
        uri = "http://192.168.7.234:5000"
    return uri
