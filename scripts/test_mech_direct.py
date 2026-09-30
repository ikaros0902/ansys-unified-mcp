import ansys.mechanical.core as mech

def test_conn():
    try:
        app = mech.Mechanical(port=10000)
        print("Connected successfully to Mechanical on port 10000!")
        res = app.run_python_script("ExtAPI.DataModel.Project.Model.Name")
        print("Model Name:", res)
    except Exception as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    test_conn()
