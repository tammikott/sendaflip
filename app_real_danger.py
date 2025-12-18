import os
import random
import subprocess
import sys
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
