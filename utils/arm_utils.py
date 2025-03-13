#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Driver final ROS pour le bras Doosan

Ce script initialise la connexion avec le robot et propose les fonctions suivantes :

- init_connection() : initialisation des services ROS et publishers nécessaires.
- pick() : commande une opération de prise à une position de grille donnée ou une position nommée.
- drop() : commande une opération de dépôt à une position de grille donnée ou une position nommée.

La grille (allant de A1 à D4) est configurée via un fichier .env dans lequel sont définies 
la position de base (A1) et les offsets par colonne et par ligne, pour la prise et pour le dépôt.

Exemple de .env :

Paramètres pour la prise
A1_PICK_X=100.0
A1_PICK_Y=200.0
A1_PICK_Z=300.0
OFFSET_PICK_COL=50.0
OFFSET_PICK_ROW=50.0

Paramètres pour le dépôt
A1_DROP_X=110.0
A1_DROP_Y=210.0
A1_DROP_Z=310.0
OFFSET_DROP_COL=50.0
OFFSET_DROP_ROW=50.0

Positions nommées
KIOSK_X=500.0
KIOSK_Y=0.0
KIOSK_Z=300.0
SCALE_X=600.0
SCALE_Y=100.0
SCALE_Z=200.0
"""

import rospy
import os
import sys
import threading
import time
from dotenv import load_dotenv

# Permet d'éviter la création de fichiers .pyc
sys.dont_write_bytecode = True

# Ajout du chemin vers le module DSR_ROBOT (issu de common/imp)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../common/imp")))
import DR_init
from DSR_ROBOT import *

# Configuration du robot
ROBOT_ID = "dsr01"
ROBOT_MODEL = "a0509"
DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL

# Chargement des variables d'environnement depuis .env
load_dotenv()

# --- Paramètres de la grille pour la prise ---
# Les parametres sont chargés depuis le fichier .env ou alors les parametres par defaut si le nom n'existe pas dans le fichier
BASE_PICK_X = float(os.getenv("A1_PICK_X", 100.0))
BASE_PICK_Y = float(os.getenv("A1_PICK_Y", 200.0))
BASE_PICK_Z = float(os.getenv("A1_PICK_Z", 300.0))
OFFSET_PICK_COL = float(os.getenv("OFFSET_PICK_COL", 50.0))
OFFSET_PICK_ROW = float(os.getenv("OFFSET_PICK_ROW", 50.0))

# --- Paramètres de la grille pour le dépôt ---
BASE_DROP_X = float(os.getenv("A1_DROP_X", 110.0))
BASE_DROP_Y = float(os.getenv("A1_DROP_Y", 210.0))
BASE_DROP_Z = float(os.getenv("A1_DROP_Z", 310.0))
OFFSET_DROP_COL = float(os.getenv("OFFSET_DROP_COL", 50.0))
OFFSET_DROP_ROW = float(os.getenv("OFFSET_DROP_ROW", 50.0))

# --- Positions nommées ---
named_positions = {}
default_positions = {
    "kiosk": (500.0, 0.0, 300.0),
    "scale": (600.0, 100.0, 200.0)
}
for name, default in default_positions.items():
    named_positions[name] = (
        float(os.getenv(f"{name.upper()}_X", default[0])),
        float(os.getenv(f"{name.upper()}_Y", default[1])),
        float(os.getenv(f"{name.upper()}_Z", default[2]))
    )

# Variables globales pour les services et publishers
pub_stop = None
set_robot_mode = None

def shutdown():
    rospy.loginfo("Shutdown time!")
    if pub_stop is not None:
        pub_stop.publish(stop_mode=STOP_TYPE_QUICK)
    return

def init_connection():
    """
    Initialise la connexion ROS avec le robot.
    Configure le service set_robot_mode et le publisher pour l'arrêt.
    """
    global pub_stop, set_robot_mode
    rospy.loginfo("[ARM] Connecting...")
    service_name = '/' + ROBOT_ID + ROBOT_MODEL + '/system/set_robot_mode'
    rospy.wait_for_service(service_name)
    set_robot_mode = rospy.ServiceProxy(service_name, SetRobotMode)
    pub_stop = rospy.Publisher('/' + ROBOT_ID + ROBOT_MODEL + '/stop', RobotStop, queue_size=10)
    rospy.loginfo("[ARM] Connection established.")
    return True

def compute_grid_position(base_x, base_y, base_z, col, row, offset_col, offset_row):
    """
    Calcule les coordonnées cibles sur la grille à partir de la position de base A1 et des offsets.
    """
    col_index = ord(col.upper()) - ord('A')
    row_index = int(row) - 1
    new_x = base_x + col_index * offset_col
    new_y = base_y + row_index * offset_row
    return new_x, new_y, base_z

def move_to_position(position, vel=30, acc=20, sol=2):
    """
    Déplace le robot vers la position cible à l'aide de movejx.
    """
    rospy.loginfo("Moving to position: {}".format(position))
    movejx(position, vel=vel, acc=acc, sol=sol)
    rospy.sleep(1)

def _pick(position):
    """
    Commande la prise d'un objet à une position de grille ou une position nommée.
    """
    if position.lower() in named_positions:
        x, y, z = named_positions[position.lower()]
    else:
        col, row = position[0], position[1:]
        x, y, z = compute_grid_position(BASE_PICK_X, BASE_PICK_Y, BASE_PICK_Z, col, row, OFFSET_PICK_COL, OFFSET_PICK_ROW)
    target = posx(x, y, z, 90, -90, -90)
    rospy.loginfo(f"[ARM] Pick à {position}")
    move_to_position(target)

def _drop(position):
    """
    Commande le dépôt d'un objet à une position de grille ou une position nommée.
    """
    if position.lower() in named_positions:
        x, y, z = named_positions[position.lower()]
    else:
        col, row = position[0], position[1:]
        x, y, z = compute_grid_position(BASE_DROP_X, BASE_DROP_Y, BASE_DROP_Z, col, row, OFFSET_DROP_COL, OFFSET_DROP_ROW)
    target = posx(x, y, z, 90, -90, -90)
    rospy.loginfo(f"[ARM] Drop à {position}")
    move_to_position(target)

def pick(line, col):
    _pick(f"{line}{col}")

def pick(named_position):
    _pick(named_position)

def drop(line, col):
    _drop(f"{line}{col}")

def drop(named_position):
    _drop(named_position)
