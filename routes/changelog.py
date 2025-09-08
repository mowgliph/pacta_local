from flask import Blueprint, render_template, redirect, url_for, session
from functools import wraps
from datetime import datetime
import requests
from database.models import Usuario, Notificacion

changelog_bp = Blueprint('changelog', __name__)

# Función helper para obtener contador de notificaciones
def get_notificaciones_count():
    """Obtiene el número de notificaciones no leídas del usuario actual"""
    if 'user_id' in session:
        return Notificacion.get_unread_count(session['user_id'])
    return 0

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@changelog_bp.route('/changelog')
@login_required
def changelog():
    """Página de changelog con historial de commits desde GitHub"""
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    commits = get_github_commits()
    spanish_summary = get_spanish_changelog_summary(commits)
    
    # Obtener información adicional
    version = "2.1.0"  # Versión actual del proyecto
    last_update = commits[0]['date'] if commits else "N/A"
    contributors = list(set([commit['author'] for commit in commits if commit.get('author')]))
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('changelog.html', 
                         commits=commits,
                         spanish_summary=spanish_summary,
                         version=version,
                         last_update=last_update,
                         contributors=contributors,
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count)

def get_github_commits():
    """Obtiene los commits desde la API de GitHub"""
    try:
        # URL de la API de GitHub para obtener commits
        url = "https://api.github.com/repos/mowgliph/pacta_local/commits"
        
        # Parámetros para la consulta
        params = {
            'per_page': 50,  # Obtener últimos 50 commits
            'sha': 'main'    # Branch principal
        }
        
        # Realizar la petición
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            commits_data = response.json()
            commits = []
            
            for commit_data in commits_data:
                # Formatear fecha
                commit_date = commit_data['commit']['author']['date']
                formatted_date = datetime.strptime(commit_date, '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M')
                
                # Extraer información del commit
                commit_info = {
                    'sha': commit_data['sha'],
                    'message': commit_data['commit']['message'].split('\n')[0],  # Solo la primera línea
                    'description': '\n'.join(commit_data['commit']['message'].split('\n')[1:]).strip() if '\n' in commit_data['commit']['message'] else None,
                    'author': commit_data['commit']['author']['name'],
                    'date': formatted_date,
                    'url': commit_data['html_url'],
                    'additions': commit_data.get('stats', {}).get('additions', 0),
                    'deletions': commit_data.get('stats', {}).get('deletions', 0),
                    'files_changed': len(commit_data.get('files', []))
                }
                
                commits.append(commit_info)
            
            return commits
        else:
            print(f"Error al obtener commits: {response.status_code}")
            return get_fallback_commits()
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener commits: {e}")
        return get_fallback_commits()
    except Exception as e:
        print(f"Error inesperado al obtener commits: {e}")
        return get_fallback_commits()

def get_fallback_commits():
    """Commits de ejemplo cuando no se puede conectar a GitHub"""
    return [
        {
            'sha': 'abc123def456',
            'message': 'Implementación inicial del sistema PACTA',
            'description': 'Sistema base con gestión de contratos, usuarios y dashboard principal.',
            'author': 'Desarrollador',
            'date': '15/01/2024 10:30',
            'url': 'https://github.com/mowgliph/pacta_local/commits/main',
            'additions': 1250,
            'deletions': 0,
            'files_changed': 25
        },
        {
            'sha': 'def456ghi789',
            'message': 'Mejoras en la interfaz de usuario',
            'description': 'Actualización del diseño y mejora de la experiencia de usuario en todas las páginas.',
            'author': 'Desarrollador',
            'date': '12/01/2024 16:45',
            'url': 'https://github.com/mowgliph/pacta_local/commits/main',
            'additions': 340,
            'deletions': 120,
            'files_changed': 8
        },
        {
            'sha': 'ghi789jkl012',
            'message': 'Configuración inicial del proyecto',
            'description': 'Estructura base del proyecto con Flask y configuración inicial.',
            'author': 'Desarrollador',
            'date': '10/01/2024 09:15',
            'url': 'https://github.com/mowgliph/pacta_local/commits/main',
            'additions': 890,
            'deletions': 0,
            'files_changed': 15
        }
    ]

def get_spanish_changelog_summary(commits):
    """Genera un resumen en español de los cambios basado en los commits"""
    if not commits:
        return "No hay commits disponibles para generar el resumen."
    
    # Categorizar commits por tipo de cambio
    features = []
    fixes = []
    improvements = []
    others = []
    
    for commit in commits[:20]:  # Analizar últimos 20 commits
        message = commit['message'].lower()
        
        if any(keyword in message for keyword in ['feat', 'feature', 'add', 'nuevo', 'nueva', 'implementa', 'agrega']):
            features.append(commit)
        elif any(keyword in message for keyword in ['fix', 'bug', 'error', 'corrige', 'soluciona', 'repara']):
            fixes.append(commit)
        elif any(keyword in message for keyword in ['improve', 'update', 'refactor', 'mejora', 'actualiza', 'optimiza']):
            improvements.append(commit)
        else:
            others.append(commit)
    
    # Generar resumen
    summary_parts = []
    
    if features:
        summary_parts.append(f"**🚀 Nuevas Funcionalidades ({len(features)}):**")
        for commit in features[:5]:  # Mostrar máximo 5
            summary_parts.append(f"• {commit['message']}")
        if len(features) > 5:
            summary_parts.append(f"• ... y {len(features) - 5} funcionalidades más")
        summary_parts.append("")
    
    if improvements:
        summary_parts.append(f"**✨ Mejoras y Optimizaciones ({len(improvements)}):**")
        for commit in improvements[:5]:
            summary_parts.append(f"• {commit['message']}")
        if len(improvements) > 5:
            summary_parts.append(f"• ... y {len(improvements) - 5} mejoras más")
        summary_parts.append("")
    
    if fixes:
        summary_parts.append(f"**🐛 Correcciones de Errores ({len(fixes)}):**")
        for commit in fixes[:5]:
            summary_parts.append(f"• {commit['message']}")
        if len(fixes) > 5:
            summary_parts.append(f"• ... y {len(fixes) - 5} correcciones más")
        summary_parts.append("")
    
    if others:
        summary_parts.append(f"**📝 Otros Cambios ({len(others)}):**")
        for commit in others[:3]:
            summary_parts.append(f"• {commit['message']}")
        if len(others) > 3:
            summary_parts.append(f"• ... y {len(others) - 3} cambios más")
    
    # Estadísticas generales
    total_additions = sum(commit.get('additions', 0) for commit in commits)
    total_deletions = sum(commit.get('deletions', 0) for commit in commits)
    total_files = sum(commit.get('files_changed', 0) for commit in commits)
    
    summary_parts.extend([
        "",
        "**📊 Estadísticas del Período:**",
        f"• Total de commits analizados: {len(commits)}",
        f"• Líneas añadidas: +{total_additions:,}",
        f"• Líneas eliminadas: -{total_deletions:,}",
        f"• Archivos modificados: {total_files:,}",
        f"• Contribuidores activos: {len(set(commit['author'] for commit in commits))}"
    ])
    
    return "\n".join(summary_parts)