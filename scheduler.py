from apscheduler.schedulers.background import BackgroundScheduler
from models.beneficiary_model import get_beneficiaries
from models.alert_model import add_alert

def scan_and_generate_alerts():
    beneficiaries = get_beneficiaries({})
    for b in beneficiaries:
        if not b.get('jjm_data', {}).get('connection_status'):
            add_alert(b["_id"], "JJM_MISSING", "No functional water connection")

        if b.get('mgnrega_data', {}).get('days_provided_fy', 0) < (b.get('mgnrega_data', {}).get('days_demanded_fy', 1) * 0.5):
            add_alert(b["_id"], "MGNREGA_LOW_WORK", "Insufficient MGNREGA work days")

        if b.get('pm_janman_data', {}).get('is_pvtg') and not b.get('pm_janman_data', {}).get('has_pucca_house'):
            add_alert(b["_id"], "PVTG_HOUSING_GAP", "PVTG family lacks pucca house")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_and_generate_alerts, 'interval', hours=24)
    scheduler.start()
