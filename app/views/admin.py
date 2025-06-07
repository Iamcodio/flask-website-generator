"""
Admin routes for lead management
"""

from flask import Blueprint, render_template, send_file, flash, redirect, url_for
import csv
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/leads')
def view_leads():
    """View collected email leads"""
    try:
        leads = []
        filename = '.dev/email_leads.csv'  # Updated path
        
        if os.path.exists(filename):
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                leads = list(reader)
        
        return render_template('leads.html', leads=leads)
    except Exception as e:
        return f"Error reading leads: {e}"

@admin_bp.route('/leads/export')
def export_leads():
    """Export leads as CSV download"""
    filename = '.dev/email_leads.csv'  # Updated path
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True, download_name='sitegen_leads.csv')
    else:
        flash('No leads file found.', 'error')
        return redirect(url_for('admin.view_leads'))