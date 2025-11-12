from flask import Flask, render_template, request, jsonify, session
import threading
import time
import os
from autolike import facebook_autolike

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "autolike-secret-key-2024")

# Stockage en mémoire (pour la démo)
active_jobs = {}

class BoostJob:
    def __init__(self, url, duration):
        self.id = str(int(time.time()))
        self.url = url
        self.duration = duration
        self.status = "running"
        self.result = None
        self.start_time = time.time()
    
    def run(self):
        try:
            # Utiliser VOTRE fonction existante
            self.result = facebook_autolike(self.url, run_time=self.duration)
            self.status = "completed"
        except Exception as e:
            self.result = {"status": "error", "message": str(e)}
            self.status = "failed"
        finally:
            self.end_time = time.time()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/start_boost', methods=['POST'])
def start_boost():
    data = request.json
    url = data.get('url', '').strip()
    duration = int(data.get('duration', 60))
    
    if not url:
        return jsonify({"error": "URL requise"}), 400
    
    # Créer un nouveau job
    job = BoostJob(url, duration)
    active_jobs[job.id] = job
    
    # Lancer dans un thread séparé
    thread = threading.Thread(target=job.run)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "job_id": job.id,
        "status": "started",
        "message": "Boost démarré avec succès"
    })

@app.route('/api/job_status/<job_id>')
def job_status(job_id):
    job = active_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job non trouvé"}), 404
    
    elapsed = int(time.time() - job.start_time)
    
    return jsonify({
        "job_id": job.id,
        "status": job.status,
        "elapsed_time": elapsed,
        "result": job.result
    })

@app.route('/api/active_jobs')
def active_jobs_list():
    jobs_info = []
    for job_id, job in active_jobs.items():
        jobs_info.append({
            "id": job_id,
            "url": job.url,
            "status": job.status,
            "duration": job.duration,
            "elapsed": int(time.time() - job.start_time)
        })
    
    return jsonify({"jobs": jobs_info})

@app.route('/api/stop_job/<job_id>', methods=['POST'])
def stop_job(job_id):
    # Dans une vraie app, vous implémenteriez l'arrêt
    return jsonify({"message": "Arrêt simulé - Refresh pour voir les résultats"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)