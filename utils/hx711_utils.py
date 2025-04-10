import time
import numpy as np
import platform

# Vérifier si on tourne sur un Raspberry Pi
if platform.machine() in ('armv7l', 'aarch64'):
    try:
        from hx711 import HX711
        HX711_AVAILABLE = True
    except ImportError:
        print("La bibliothèque HX711 n'est pas disponible.")
        HX711_AVAILABLE = False
else:
    print("Balance HX711 non supportée sur cette plateforme.")
    HX711_AVAILABLE = False

class MockHX711:
    """Classe mock pour l'environnement de développement"""
    def __init__(self, *args, **kwargs):
        print("⚠️ Utilisation du mock HX711 (environnement de développement)")
        self.calibration_factor = 1.03
        self.offset_tare = 0
        self.estimation = 0
        self.P = 1
        self.Q = 0.05
        self.R = 0.5
    
    def is_ready(self):
        return True
    
    def tare(self):
        print("Mock: Tare effectuée")
    
    def get_units(self, samples=1):
        return 1000  # Valeur de test
    
    def power_down(self):
        pass
    
    def power_up(self):
        pass

class HX711Driver:
    def __init__(self, dout_pin=32, pd_sck_pin=31):
        if HX711_AVAILABLE:
            self.hx = HX711(dout_pin, pd_sck_pin)
        else:
            self.hx = MockHX711()
            
        self.calibration_factor = 1.03
        self.offset_tare = 0
        
        # Paramètres du filtre de Kalman
        self.estimation = 0
        self.P = 1
        self.Q = 0.05  # Bruit du processus
        self.R = 0.5   # Bruit de mesure
        
        self._setup()
    
    def _setup(self):
        """Initialisation du capteur HX711"""
        print("🔧 Initialisation HX711...")
        self.hx.tare()
        time.sleep(0.5)
        self.offset_tare = self.hx.get_units(10)
        print(f"📊 Offset tare : {self.offset_tare}")
    
    def kalman_update(self, measurement):
        """Mise à jour du filtre de Kalman"""
        # Vérification d'une variation brutale
        error = measurement - self.estimation
        if abs(error) > 50:  # seuil ajustable selon l'unité
            self.estimation = measurement
            self.P = 1  # réinitialise la covariance d'erreur
            return self.estimation
        
        # Mise à jour standard du filtre Kalman
        self.P += self.Q
        K = self.P / (self.P + self.R)
        self.estimation = self.estimation + K * (measurement - self.estimation)
        self.P = (1 - K) * self.P
        return self.estimation
    
    def calibrate(self, known_weight):
        """Calibration avec un poids connu"""
        print("⚖️ Pose un objet de poids connu sur la balance...")
        time.sleep(3)  # attendre la stabilisation
        
        raw_value = self.hx.get_units(10)
        print(f"📈 Valeur brute mesurée : {raw_value}")
        
        self.calibration_factor = (raw_value - self.offset_tare) / known_weight
        print(f"✅ Facteur de calibration calculé : {self.calibration_factor:.4f}")
    
    def get_weight(self, samples=5):
        """Obtention du poids filtré en grammes"""
        raw_weight = (self.hx.get_units(samples) - self.offset_tare) / self.calibration_factor
        filtered_weight = self.kalman_update(raw_weight)
        return filtered_weight / 1000.0  # conversion en grammes
    
    def tare(self):
        """Remise à zéro de la balance"""
        self.hx.tare()
        time.sleep(0.5)
        self.offset_tare = self.hx.get_units(10)
        print(f"📊 Nouvel offset tare : {self.offset_tare}")

# Exemple d'utilisation
if __name__ == "__main__":
    scale = HX711Driver()
    
    # Calibration (à décommenter si nécessaire)
    # scale.calibrate(500)  # 500g de poids connu
    
    print("⏺️ Acquisition des données en cours...")
    print("time_ms,poids_g")
    
    try:
        while True:
            weight = scale.get_weight()
            print(f"{int(time.time() * 1000)},{weight:.3f}")
            time.sleep(0.01)  # fréquence d'échantillonnage de 100 Hz
    except KeyboardInterrupt:
        print("\nArrêt de l'acquisition") 