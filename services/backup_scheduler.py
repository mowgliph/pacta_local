import atexit
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from services.backup_service import BackupService
from services.change_detection_service import ChangeDetectionService
import logging

# Configurar logging para APScheduler
logging.getLogger('apscheduler').setLevel(logging.INFO)

class BackupScheduler:
    def __init__(self):
        self.backup_service = BackupService()
        self.change_detection = ChangeDetectionService()
        
        # Configurar el scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': ThreadPoolExecutor(max_workers=1)  # Solo un backup a la vez
        }
        
        job_defaults = {
            'coalesce': True,  # Combinar trabajos pendientes
            'max_instances': 1,  # Solo una instancia del trabajo
            'misfire_grace_time': 300  # 5 minutos de gracia para trabajos perdidos
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='America/Havana'  # Ajustar según la zona horaria
        )
        
        self._setup_jobs()
        
        # Registrar función de limpieza al salir
        atexit.register(self.shutdown)
    
    def _setup_jobs(self):
        """
        Configura los trabajos programados
        """
        # Backup automático diario a las 4 PM
        self.scheduler.add_job(
            func=self._daily_backup_job,
            trigger=CronTrigger(hour=16, minute=0),  # 4:00 PM
            id='daily_backup',
            name='Backup Automático Diario',
            replace_existing=True
        )
        
        # Limpieza de backups obsoletos diaria a las 5 AM
        self.scheduler.add_job(
            func=self._cleanup_old_backups_job,
            trigger=CronTrigger(hour=5, minute=0),  # 5:00 AM
            id='cleanup_backups',
            name='Limpieza de Backups Obsoletos',
            replace_existing=True
        )
        
        # Limpieza de registros de cambios semanalmente
        self.scheduler.add_job(
            func=self._cleanup_change_records_job,
            trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),  # Domingos a las 3 AM
            id='cleanup_changes',
            name='Limpieza de Registros de Cambios',
            replace_existing=True
        )
    
    def _daily_backup_job(self):
        """
        Trabajo programado para backup diario
        Solo se ejecuta si hay cambios pendientes
        """
        try:
            print(f"[{datetime.now()}] Iniciando verificación de backup automático...")
            
            # Verificar si hay cambios pendientes
            changes_info = self.change_detection.has_changes_since_last_backup()
            
            if not changes_info.get('has_changes', False):
                print(f"[{datetime.now()}] No hay cambios pendientes. Backup automático omitido.")
                return
            
            print(f"[{datetime.now()}] Se encontraron {changes_info.get('total_changes', 0)} cambios. Iniciando backup...")
            
            # Crear backup automático
            backup_result = self.backup_service.create_backup(
                backup_type='automatic',
                reason=f"Backup automático - {changes_info.get('total_changes', 0)} cambios detectados"
            )
            
            if backup_result.get('success', False):
                print(f"[{datetime.now()}] Backup automático completado exitosamente: {backup_result['backup_info']['name']}")
                
                # Marcar cambios como procesados
                mark_result = self.change_detection.mark_changes_as_processed()
                if mark_result.get('success', False):
                    print(f"[{datetime.now()}] Se marcaron {mark_result.get('processed_count', 0)} cambios como procesados")
                
            else:
                print(f"[{datetime.now()}] Error en backup automático: {backup_result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"[{datetime.now()}] Error en trabajo de backup automático: {str(e)}")
    
    def _cleanup_old_backups_job(self):
        """
        Trabajo programado para limpiar backups obsoletos
        """
        try:
            print(f"[{datetime.now()}] Iniciando limpieza de backups obsoletos...")
            
            # Mantener backups de los últimos 7 días, pero conservar al menos 3 backups
            cleanup_result = self.backup_service.cleanup_old_backups(retention_days=7, keep_minimum=3)
            
            if cleanup_result.get('success', False):
                deleted_count = cleanup_result.get('deleted_count', 0)
                print(f"[{datetime.now()}] Limpieza completada: {deleted_count} backups eliminados")
            else:
                print(f"[{datetime.now()}] Error en limpieza de backups: {cleanup_result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"[{datetime.now()}] Error en trabajo de limpieza de backups: {str(e)}")
    
    def _cleanup_change_records_job(self):
        """
        Trabajo programado para limpiar registros de cambios antiguos
        """
        try:
            print(f"[{datetime.now()}] Iniciando limpieza de registros de cambios...")
            
            cleanup_result = self.change_detection.cleanup_old_changes(days=30)
            
            if cleanup_result.get('success', False):
                deleted_count = cleanup_result.get('deleted_count', 0)
                print(f"[{datetime.now()}] Limpieza de registros completada: {deleted_count} registros eliminados")
            else:
                print(f"[{datetime.now()}] Error en limpieza de registros: {cleanup_result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"[{datetime.now()}] Error en trabajo de limpieza de registros: {str(e)}")
    
    def start(self):
        """
        Inicia el scheduler
        """
        if not self.scheduler.running:
            self.scheduler.start()
            print(f"[{datetime.now()}] Scheduler de backups iniciado")
            self._print_scheduled_jobs()
    
    def shutdown(self):
        """
        Detiene el scheduler de forma segura
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            print(f"[{datetime.now()}] Scheduler de backups detenido")
    
    def _print_scheduled_jobs(self):
        """
        Imprime información sobre los trabajos programados
        """
        jobs = self.scheduler.get_jobs()
        print(f"[{datetime.now()}] Trabajos programados:")
        for job in jobs:
            next_run = job.next_run_time
            print(f"  - {job.name}: próxima ejecución {next_run}")
    
    def get_job_status(self):
        """
        Obtiene el estado de los trabajos programados
        """
        try:
            jobs_info = []
            jobs = self.scheduler.get_jobs()
            
            for job in jobs:
                jobs_info.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            
            return {
                'success': True,
                'scheduler_running': self.scheduler.running,
                'jobs': jobs_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def trigger_manual_backup(self):
        """
        Ejecuta un backup manual inmediatamente
        """
        try:
            print(f"[{datetime.now()}] Iniciando backup manual...")
            
            backup_result = self.backup_service.create_backup(
                backup_type='manual',
                reason='Backup manual solicitado por usuario'
            )
            
            if backup_result.get('success', False):
                print(f"[{datetime.now()}] Backup manual completado: {backup_result['backup_info']['name']}")
                
                # Marcar cambios como procesados también para backups manuales
                self.change_detection.mark_changes_as_processed()
            
            return backup_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error en backup manual: {str(e)}'
            }
    
    def reschedule_daily_backup(self, hour: int = 16, minute: int = 0):
        """
        Reprograma el backup diario a una hora diferente
        
        Args:
            hour: Hora del día (0-23)
            minute: Minuto de la hora (0-59)
        """
        try:
            # Eliminar el trabajo existente
            self.scheduler.remove_job('daily_backup')
            
            # Crear nuevo trabajo con la nueva hora
            self.scheduler.add_job(
                func=self._daily_backup_job,
                trigger=CronTrigger(hour=hour, minute=minute),
                id='daily_backup',
                name='Backup Automático Diario',
                replace_existing=True
            )
            
            return {
                'success': True,
                'message': f'Backup diario reprogramado para las {hour:02d}:{minute:02d}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Instancia global del scheduler
_backup_scheduler = None

def get_backup_scheduler():
    """
    Obtiene la instancia global del scheduler
    """
    global _backup_scheduler
    if _backup_scheduler is None:
        _backup_scheduler = BackupScheduler()
    return _backup_scheduler

def start_backup_scheduler():
    """
    Inicia el scheduler de backups
    """
    scheduler = get_backup_scheduler()
    scheduler.start()
    return scheduler