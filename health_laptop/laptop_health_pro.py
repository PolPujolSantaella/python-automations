import psutil
import tkinter as tk
import socket
from tkinter import ttk
from plyer import notification
import json
import os
from datetime import datetime, timedelta
import time

class LaptopHealthMonitor:
    def __init__(self):
        self.config_file = "health_config.json"
        self.history_file = "health_history.json"
        self.config = self.load_config()
        self.load_history()
    
    def load_config(self):
        """Carga configuración personalizable"""
        default_config = {
            "thresholds": {
                "cpu_warning": 80,
                "ram_warning": 85,
                "disk_warning": 90,
                "battery_low": 20
            },
            "notifications": True,
            "auto_refresh": True,
            "refresh_interval": 5000  # milliseconds
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except:
                return default_config
        return default_config
    
    def save_config(self):
        """Guarda la configuración actual"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def load_history(self):
        """Carga historial de métricas"""
        self.history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def save_to_history(self, stats):
        """Guarda métricas actuales al historial"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "cpu": stats[0],
            "ram": stats[1],
            "disk": stats[2],
            "battery": stats[3],
            "battery_status": stats[4]
        }
        
        self.history.append(entry)
        
        # Mantener solo últimos 30 días
        cutoff_date = datetime.now() - timedelta(days=30)
        self.history = [h for h in self.history if datetime.fromisoformat(h["timestamp"]) > cutoff_date]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def get_system_stats(self):
        """Obtener estadísticas del sistema con manejo de errores mejorado"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            
            # Manejo multiplataforma para disco
            try:
                if os.name == 'nt':  # Windows
                    disk = psutil.disk_usage('C:\\').percent
                else:  # Unix/Linux/Mac
                    disk = psutil.disk_usage('/').percent
            except:
                disk = 0
            
            # Información de batería con mejor manejo de errores
            try:
                battery_info = psutil.sensors_battery()
                if battery_info:
                    battery = battery_info.percent
                    status = "🔌 Cargando" if battery_info.power_plugged else "🔋 Desconectado"
                else:
                    battery = 0
                    status = "🖥️ PC de Escritorio"
            except:
                battery = 0
                status = "❓ No disponible"
            
            # Información adicional
            temps = self.get_temperature()
            network = self.get_network_stats()
            
            return cpu, ram, disk, battery, status, temps, network
        
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return 0, 0, 0, 0, "Error", {}, {}
    
    def get_temperature(self):
        """Obtiene temperatura del sistema (si está disponible)"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                avg_temps = {}
                for name, entries in temps.items():
                    if entries:
                        avg_temp = sum(entry.current for entry in entries) / len(entries)
                        avg_temps[name] = round(avg_temp, 1)
                return avg_temps
        except:
            pass
        return {}
    
    def get_network_stats(self):
        """Obtiene estadísticas de red más completas"""
        net_info = {}
        try:
            # Bytes totales enviados/recibidos
            net = psutil.net_io_counters()
            net_info["bytes_sent"] = self.format_bytes(net.bytes_sent)
            net_info["bytes_recv"] = self.format_bytes(net.bytes_recv)

            # Velocidad de subida/bajada (instantánea)
            net1 = psutil.net_io_counters()
            time.sleep(1)
            net2 = psutil.net_io_counters()
            net_info["upload_speed"] = self.format_bytes(net2.bytes_sent - net1.bytes_sent) + "/s"
            net_info["download_speed"] = self.format_bytes(net2.bytes_recv - net1.bytes_recv) + "/s"

            # Ping a Google DNS
            try:
                start = time.time()
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                latency = round((time.time() - start) * 1000)  # ms
                net_info["latency"] = f"{latency} ms"
                net_info["status"] = "Buena conexión" if latency < 100 else "Conexión lenta"
            except:
                net_info["latency"] = "N/A"
                net_info["status"] = "Sin conexión"
            
        except Exception as e:
            net_info = {
                "bytes_sent": "N/A",
                "bytes_recv": "N/A",
                "upload_speed": "N/A",
                "download_speed": "N/A",
                "latency": "N/A",
                "status": "Error"
            }
        
        return net_info
    
    def format_bytes(self, bytes_value):
        """Convierte bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def get_health_status(self, cpu, ram, disk, battery):
        """Determina el estado general de salud"""
        issues = []
        
        if cpu > self.config["thresholds"]["cpu_warning"]:
            issues.append(f"🔥 CPU alta ({cpu}%)")
        
        if ram > self.config["thresholds"]["ram_warning"]:
            issues.append(f"🧠 RAM alta ({ram}%)")
        
        if disk > self.config["thresholds"]["disk_warning"]:
            issues.append(f"💾 Disco lleno ({disk}%)")
        
        if battery < self.config["thresholds"]["battery_low"] and battery > 0:
            issues.append(f"🪫 Batería baja ({battery}%)")
        
        if not issues:
            return "✅ Excelente", "#4caf50"
        elif len(issues) == 1:
            return f"⚠️ {issues[0]}", "#ff9800"
        else:
            return f"🚨 {len(issues)} problemas detectados", "#f44336"

    def send_popup(self, cpu, ram, disk, battery, status):
        """Enviar notificación con información de salud mejorada"""
        if not self.config["notifications"]:
            return
        
        health_status, _ = self.get_health_status(cpu, ram, disk, battery)
        
        message = f"""Estado: {health_status}
        
CPU: {cpu}% | RAM: {ram}%
Disco: {disk}% | Batería: {battery}%
Estado: {status}"""
        
        notification.notify(
            title="💻 Reporte de Salud - Laptop",
            message=message,
            timeout=15
        )

    def create_modern_window(self, stats):
        """Crear ventana moderna con más funcionalidades"""
        cpu, ram, disk, battery, status, temps, network = stats
        
        self.window = tk.Tk()
        self.window.title("🖥️ Monitor de Salud - Laptop")
        self.window.geometry("500x700")
        self.window.configure(bg="#0d1117")
        self.window.resizable(True, True)
        
        # Configurar estilo una sola vez
        self.setup_styles()
        
        # Scrollable frame
        canvas = tk.Canvas(self.window, bg="#0d1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header con estado de salud
        health_status, health_color = self.get_health_status(cpu, ram, disk, battery)
        header_frame = tk.Frame(scrollable_frame, bg="#0d1117")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header_frame, text="🖥️ Monitor de Salud", 
                font=("Segoe UI", 18, "bold"), bg="#0d1117", fg="#f0f6fc").pack()
        
        tk.Label(header_frame, text=health_status, 
                font=("Segoe UI", 14), bg="#0d1117", fg=health_color).pack(pady=5)
        
        tk.Label(header_frame, text=f"Actualizado: {datetime.now().strftime('%H:%M:%S')}", 
                font=("Segoe UI", 10), bg="#0d1117", fg="#8b949e").pack()
        
        # Métricas principales
        metrics_frame = tk.Frame(scrollable_frame, bg="#0d1117")
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        metrics = [
            ("CPU", cpu, "#ff6b6b", "🔥"),
            ("RAM", ram, "#4ecdc4", "🧠"), 
            ("Disco", disk, "#ffd93d", "💾"),
            ("Batería", battery, "#1fa2ff", "🔋")
        ]
        
        for i, (name, value, color, icon) in enumerate(metrics):
            self.create_metric_widget(metrics_frame, name, value, color, icon, i)
        
        # Información adicional
        if status != "🖥️ PC de Escritorio":
            info_frame = tk.Frame(scrollable_frame, bg="#161b22", relief="raised", bd=1)
            info_frame.pack(fill="x", padx=20, pady=5)
            tk.Label(info_frame, text=f"Estado Batería: {status}", 
                    font=("Segoe UI", 11), bg="#161b22", fg="#f0f6fc").pack(pady=5)
        
        # Temperaturas (si están disponibles)
        if temps:
            temp_frame = tk.LabelFrame(scrollable_frame, text="🌡️ Temperaturas", 
                                     bg="#0d1117", fg="#f0f6fc", font=("Segoe UI", 12, "bold"))
            temp_frame.pack(fill="x", padx=20, pady=5)
            
            for sensor, temp in temps.items():
                color = "#4caf50" if temp < 70 else "#ff9800" if temp < 80 else "#f44336"
                tk.Label(temp_frame, text=f"{sensor}: {temp}°C", 
                        font=("Segoe UI", 10), bg="#0d1117", fg=color).pack(pady=2)
        
        # Red (si está disponible)
        if network:
            net_frame = tk.LabelFrame(scrollable_frame, text="🌐 Red", 
                                    bg="#0d1117", fg="#f0f6fc", font=("Segoe UI", 12, "bold"))
            net_frame.pack(fill="x", padx=20, pady=5)

            tk.Label(net_frame, text=f"Enviado: {network.get('bytes_sent','N/A')}", font=("Segoe UI", 10),
                    bg="#0d1117", fg="#f0f6fc").pack(pady=2)
            tk.Label(net_frame, text=f"Recibido: {network.get('bytes_recv','N/A')}", font=("Segoe UI", 10),
                    bg="#0d1117", fg="#f0f6fc").pack(pady=2)
            tk.Label(net_frame, text=f"Velocidad subida: {network.get('upload_speed','N/A')}", font=("Segoe UI", 10),
                    bg="#0d1117", fg="#f0f6fc").pack(pady=2)
            tk.Label(net_frame, text=f"Velocidad bajada: {network.get('download_speed','N/A')}", font=("Segoe UI", 10),
                    bg="#0d1117", fg="#f0f6fc").pack(pady=2)
            tk.Label(net_frame, text=f"Latencia: {network.get('latency','N/A')}", font=("Segoe UI", 10),
                    bg="#0d1117", fg="#f0f6fc").pack(pady=2)
            tk.Label(net_frame, text=f"Estado: {network.get('status','N/A')}", font=("Segoe UI", 10, "bold"),
                    bg="#0d1117", fg="#4caf50" if network.get('status')=="Buena conexión" else "#ff9800").pack(pady=2)
        
        # Controles
        controls_frame = tk.Frame(scrollable_frame, bg="#0d1117")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        refresh_btn = tk.Button(controls_frame, text="🔄 Actualizar", 
                               font=("Segoe UI", 11), bg="#238636", fg="white",
                               command=self.refresh_data, relief="flat")
        refresh_btn.pack(side="left", padx=5)
        
        config_btn = tk.Button(controls_frame, text="⚙️ Configurar", 
                              font=("Segoe UI", 11), bg="#1f6feb", fg="white",
                              command=self.open_settings, relief="flat")
        config_btn.pack(side="left", padx=5)
        
        history_btn = tk.Button(controls_frame, text="📊 Historial", 
                               font=("Segoe UI", 11), bg="#8957e5", fg="white",
                               command=self.show_history, relief="flat")
        history_btn.pack(side="left", padx=5)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Auto-refresh si está habilitado
        #if self.config["auto_refresh"]:
        #    self.window.after(self.config["refresh_interval"], self.auto_refresh)
        
        # Guardar estadísticas al historial
        self.save_to_history(stats)
        
        self.window.mainloop()
    
    def setup_styles(self):
        """Configurar estilos de tkinter una sola vez"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
    
    def create_metric_widget(self, parent, name, value, color, icon, index):
        """Crea widget individual para cada métrica"""
        frame = tk.Frame(parent, bg="#161b22", relief="raised", bd=1)
        frame.pack(fill="x", pady=5)
        
        header_frame = tk.Frame(frame, bg="#161b22")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header_frame, text=f"{icon} {name}: {value}%", 
                font=("Segoe UI", 12, "bold"), bg="#161b22", fg="#f0f6fc").pack(anchor="w")
        
        # Crear canvas personalizado para la barra de progreso
        canvas = tk.Canvas(frame, height=25, bg="#161b22", highlightthickness=0)
        canvas.pack(fill="x", padx=10, pady=(0, 10))
        
        def draw_progress_bar():
            canvas.delete("all")
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Solo dibujar si el canvas tiene tamaño
                # Fondo de la barra
                canvas.create_rectangle(5, 5, canvas_width-5, 20, 
                                      fill="#21262d", outline="#30363d", width=1)
                
                # Barra de progreso
                progress_width = int((canvas_width - 10) * (value / 100))
                if progress_width > 0:
                    canvas.create_rectangle(5, 5, 5 + progress_width, 20, 
                                          fill=color, outline="", width=0)
                
                # Texto del porcentaje
                canvas.create_text(canvas_width//2, 12, text=f"{value}%", 
                                 fill="white", font=("Segoe UI", 9, "bold"))
        
        # Configurar el dibujo cuando el canvas esté listo
        canvas.bind('<Configure>', lambda e: draw_progress_bar())
        canvas.after(1, draw_progress_bar)  # Dibujar inicial
    
    def refresh_data(self):
        """Actualizar datos manualmente"""
        self.window.destroy()
        self.run()
    
    def auto_refresh(self):
        """Auto-actualización de datos"""
        if hasattr(self, 'window') and self.window.winfo_exists():
            self.refresh_data()
    
    def open_settings(self):
        """Abrir ventana de configuración"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("⚙️ Configuración")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#0d1117")
        
        # Aquí podrías agregar controles para modificar self.config
        tk.Label(settings_window, text="Configuración próximamente...", 
                font=("Segoe UI", 14), bg="#0d1117", fg="#f0f6fc").pack(expand=True)
    
    def show_history(self):
        """Mostrar historial básico"""
        history_window = tk.Toplevel(self.window)
        history_window.title("📊 Historial")
        history_window.geometry("500x400")
        history_window.configure(bg="#0d1117")
        
        if self.history:
            latest_entries = self.history[-10:]  # Últimos 10 registros
            
            text_widget = tk.Text(history_window, bg="#161b22", fg="#f0f6fc", 
                                font=("Courier", 10))
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            
            text_widget.insert(tk.END, "HISTORIAL RECIENTE:\n\n")
            
            for entry in latest_entries:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                text_widget.insert(tk.END, f"📅 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                text_widget.insert(tk.END, f"CPU: {entry['cpu']}% | RAM: {entry['ram']}% | ")
                text_widget.insert(tk.END, f"Disco: {entry['disk']}% | Batería: {entry['battery']}%\n\n")
            
            text_widget.config(state="disabled")
        else:
            tk.Label(history_window, text="No hay historial disponible", 
                    font=("Segoe UI", 14), bg="#0d1117", fg="#f0f6fc").pack(expand=True)
    
    def run(self):
        """Ejecutar el monitor"""
        stats = self.get_system_stats()
        
        # Enviar notificación
        self.send_popup(*stats[:5])
        
        # Crear ventana
        self.create_modern_window(stats)

# -------------------------------
# Ejecutar
# -------------------------------
if __name__ == "__main__":
    monitor = LaptopHealthMonitor()
    monitor.run()