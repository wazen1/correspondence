"""
Advanced Analytics with Machine Learning for Correspondence App
Provides predictive analytics, trend analysis, and intelligent insights
"""

import frappe
from frappe import _
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
from datetime import datetime, timedelta
import json


class CorrespondenceAnalytics:
	"""Advanced analytics engine for correspondence management"""
	
	def __init__(self):
		self.label_encoders = {}
	
	def predict_response_time(self, doctype, docname):
		"""
		Predict expected response time for a letter
		
		Args:
			doctype: Document type
			docname: Document name
			
		Returns:
			dict: Predicted response time in days
		"""
		try:
			# Get historical data
			historical_data = self._get_historical_response_data(doctype)
			
			if len(historical_data) < 10:
				return {
					"success": False,
					"message": _("Insufficient historical data for prediction")
				}
			
			# Prepare features
			X, y = self._prepare_response_time_features(historical_data)
			
			# Train model
			model = GradientBoostingRegressor(n_estimators=100, random_state=42)
			model.fit(X, y)
			
			# Get current document features
			current_doc = frappe.get_doc(doctype, docname)
			current_features = self._extract_document_features(current_doc)
			
			# Predict
			predicted_days = model.predict([current_features])[0]
			
			return {
				"success": True,
				"predicted_response_days": round(predicted_days, 1),
				"expected_response_date": (datetime.now() + timedelta(days=predicted_days)).strftime("%Y-%m-%d"),
				"confidence": "medium" if len(historical_data) < 50 else "high"
			}
			
		except Exception as e:
			frappe.log_error(f"Error predicting response time: {str(e)}", "Analytics Error")
			return {
				"success": False,
				"message": str(e)
			}
	
	def predict_priority(self, doctype, docname):
		"""
		Predict priority level for a letter based on content and metadata
		
		Args:
			doctype: Document type
			docname: Document name
			
		Returns:
			dict: Predicted priority
		"""
		try:
			# Get historical data
			historical_data = self._get_historical_priority_data(doctype)
			
			if len(historical_data) < 20:
				return {
					"success": False,
					"message": _("Insufficient historical data for prediction")
				}
			
			# Prepare features
			X, y = self._prepare_priority_features(historical_data)
			
			# Train model
			model = RandomForestClassifier(n_estimators=100, random_state=42)
			model.fit(X, y)
			
			# Get current document features
			current_doc = frappe.get_doc(doctype, docname)
			current_features = self._extract_document_features(current_doc)
			
			# Predict
			predicted_priority_idx = model.predict([current_features])[0]
			predicted_proba = model.predict_proba([current_features])[0]
			
			# Decode priority
			priority_levels = ["Low", "Medium", "High", "Urgent"]
			predicted_priority = priority_levels[predicted_priority_idx]
			confidence = max(predicted_proba)
			
			return {
				"success": True,
				"predicted_priority": predicted_priority,
				"confidence": round(confidence * 100, 1),
				"probabilities": {
					level: round(prob * 100, 1) 
					for level, prob in zip(priority_levels, predicted_proba)
				}
			}
			
		except Exception as e:
			frappe.log_error(f"Error predicting priority: {str(e)}", "Analytics Error")
			return {
				"success": False,
				"message": str(e)
			}
	
	def analyze_trends(self, doctype, period_days=90):
		"""
		Analyze correspondence trends over time
		
		Args:
			doctype: Document type
			period_days: Number of days to analyze
			
		Returns:
			dict: Trend analysis results
		"""
		try:
			start_date = datetime.now() - timedelta(days=period_days)
			
			# Get data
			date_field = "date_received" if doctype == "Incoming Letter" else "date_sent"
			
			letters = frappe.get_all(
				doctype,
				filters={
					date_field: [">=", start_date.strftime("%Y-%m-%d")]
				},
				fields=["name", date_field, "status", "priority", "department"]
			)
			
			if not letters:
				return {
					"success": False,
					"message": _("No data available for the specified period")
				}
			
			# Convert to DataFrame
			df = pd.DataFrame([dict(d) for d in letters])
			df[date_field] = pd.to_datetime(df[date_field])
			
			# Calculate trends
			trends = {
				"total_letters": int(len(letters)),
				"daily_average": float(round(len(letters) / period_days, 2)),
				"by_status": {k: int(v) for k, v in df["status"].value_counts().to_dict().items()},
				"by_priority": {k: int(v) for k, v in df["priority"].value_counts().to_dict().items()},
				"by_department": {k: int(v) for k, v in df["department"].value_counts().to_dict().items()} if "department" in df.columns else {},
				"weekly_trend": self._calculate_weekly_trend(df, date_field),
				"growth_rate": self._calculate_growth_rate(df, date_field)
			}
			
			return {
				"success": True,
				"period_days": period_days,
				"trends": trends
			}
			
		except Exception as e:
			frappe.log_error(f"Error analyzing trends: {str(e)}", "Analytics Error")
			return {
				"success": False,
				"message": str(e)
			}
	
	def identify_bottlenecks(self, doctype):
		"""
		Identify bottlenecks in correspondence processing
		
		Args:
			doctype: Document type
			
		Returns:
			dict: Bottleneck analysis
		"""
		try:
			# Get pending/in-progress letters
			pending_letters = frappe.get_all(
				doctype,
				filters={
					"status": ["in", ["Pending", "In Progress", "Under Review", "Draft", "Under Process", "Waiting"]]
				},
				fields=["name", "status", "department", "creation", "modified"]
			)
			
			if not pending_letters:
				return {
					"success": True,
					"message": _("No bottlenecks detected"),
					"bottlenecks": []
				}
			
			# Analyze bottlenecks
			bottlenecks = []
			
			# By department
			dept_counts = {}
			for letter in pending_letters:
				dept = letter.get("department", "Unassigned")
				dept_counts[dept] = dept_counts.get(dept, 0) + 1
			
			# Find departments with high pending count
			avg_pending = sum(dept_counts.values()) / len(dept_counts) if dept_counts else 0
			for dept, count in dept_counts.items():
				if count > avg_pending * 1.5:
					bottlenecks.append({
						"type": "department",
						"name": dept,
						"pending_count": count,
						"severity": "high" if count > avg_pending * 2 else "medium"
					})
			
			# By age
			now = datetime.now()
			old_letters = [
				letter for letter in pending_letters
				if (now - letter.get("creation")).days > 7
			]
			
			if len(old_letters) > len(pending_letters) * 0.3:
				bottlenecks.append({
					"type": "aging",
					"name": "Old pending letters",
					"count": len(old_letters),
					"severity": "high"
				})
			
			return {
				"success": True,
				"total_pending": len(pending_letters),
				"bottlenecks": bottlenecks
			}
			
		except Exception as e:
			frappe.log_error(f"Error identifying bottlenecks: {str(e)}", "Analytics Error")
			return {
				"success": False,
				"message": str(e)
			}
	
	def generate_insights(self, doctype):
		"""
		Generate intelligent insights about correspondence
		
		Args:
			doctype: Document type
			
		Returns:
			dict: Generated insights
		"""
		try:
			insights = []
			
			# Get recent data (last 30 days)
			thirty_days_ago = datetime.now() - timedelta(days=30)
			date_field = "date_received" if doctype == "Incoming Letter" else "date_sent"
			
			recent_letters = frappe.get_all(
				doctype,
				filters={
					date_field: [">=", thirty_days_ago.strftime("%Y-%m-%d")]
				},
				fields=["name", "status", "priority", "department", date_field]
			)
			
			if not recent_letters:
				return {
					"success": True,
					"insights": [{"type": "info", "message": _("No recent data available")}]
				}
			
			# Insight 1: Volume change
			prev_period = frappe.get_all(
				doctype,
				filters={
					date_field: ["between", [
						(thirty_days_ago - timedelta(days=30)).strftime("%Y-%m-%d"),
						thirty_days_ago.strftime("%Y-%m-%d")
					]]
				}
			)
			
			volume_change = ((len(recent_letters) - len(prev_period)) / len(prev_period) * 100) if prev_period else 0
			
			if abs(volume_change) > 20:
				insights.append({
					"type": "trend",
					"severity": "high" if volume_change > 50 else "medium",
					"message": _("Letter volume has {0} by {1}%").format(
						"increased" if volume_change > 0 else "decreased",
						abs(round(volume_change, 1))
					)
				})
			
			# Insight 2: Priority distribution
			high_priority = [l for l in recent_letters if l.get("priority") in ["High", "Urgent"]]
			if len(high_priority) > len(recent_letters) * 0.4:
				insights.append({
					"type": "alert",
					"severity": "high",
					"message": _("{0}% of recent letters are high priority").format(
						round(len(high_priority) / len(recent_letters) * 100, 1)
					)
				})
			
			# Insight 3: Completion rate
			completed = [l for l in recent_letters if l.get("status") == "Completed"]
			completion_rate = len(completed) / len(recent_letters) * 100
			
			if completion_rate < 50:
				insights.append({
					"type": "warning",
					"severity": "medium",
					"message": _("Completion rate is low at {0}%").format(round(completion_rate, 1))
				})
			elif completion_rate > 80:
				insights.append({
					"type": "success",
					"severity": "low",
					"message": _("Excellent completion rate of {0}%").format(round(completion_rate, 1))
				})
			
			return {
				"success": True,
				"insights": insights,
				"summary": {
					"total_recent": len(recent_letters),
					"completion_rate": round(completion_rate, 1),
					"high_priority_count": len(high_priority)
				}
			}
			
		except Exception as e:
			frappe.log_error(f"Error generating insights: {str(e)}", "Analytics Error")
			return {
				"success": False,
				"message": str(e)
			}
	
	def _get_historical_response_data(self, doctype):
		"""Get historical data for response time prediction"""
		# Get completed letters with response times
		letters = frappe.db.sql("""
			SELECT 
				name, priority, department, 
				DATEDIFF(modified, creation) as response_days
			FROM `tab{0}`
			WHERE status = 'Completed'
			AND DATEDIFF(modified, creation) > 0
			LIMIT 1000
		""".format(doctype), as_dict=True)
		
		return letters
	
	def _get_historical_priority_data(self, doctype):
		"""Get historical data for priority prediction"""
		letters = frappe.get_all(
			doctype,
			fields=["name", "priority", "department", "status"],
			limit=1000
		)
		return letters
	
	def _prepare_response_time_features(self, data):
		"""Prepare features for response time prediction"""
		df = pd.DataFrame(data)
		
		# Encode categorical variables
		if "priority" in df.columns:
			priority_map = {"Low": 0, "Medium": 1, "High": 2, "Urgent": 3}
			df["priority_encoded"] = df["priority"].map(priority_map)
		
		if "department" in df.columns:
			le = LabelEncoder()
			df["department_encoded"] = le.fit_transform(df["department"])
			self.label_encoders["department"] = le
		
		# Features and target
		X = df[["priority_encoded", "department_encoded"]].values
		y = df["response_days"].values
		
		return X, y
	
	def _prepare_priority_features(self, data):
		"""Prepare features for priority prediction"""
		df = pd.DataFrame(data)
		
		# Encode categorical variables
		if "department" in df.columns:
			le = LabelEncoder()
			df["department_encoded"] = le.fit_transform(df["department"])
		
		if "status" in df.columns:
			status_map = {"Draft": 0, "Pending": 1, "In Progress": 2, "Completed": 3}
			df["status_encoded"] = df["status"].map(status_map)
		
		# Map priority to numeric
		priority_map = {"Low": 0, "Medium": 1, "High": 2, "Urgent": 3}
		df["priority_encoded"] = df["priority"].map(priority_map)
		
		# Features and target
		X = df[["department_encoded", "status_encoded"]].values
		y = df["priority_encoded"].values
		
		return X, y
	
	def _extract_document_features(self, doc):
		"""Extract features from a document for prediction"""
		features = []
		
		# Priority
		priority_map = {"Low": 0, "Medium": 1, "High": 2, "Urgent": 3}
		features.append(priority_map.get(getattr(doc, "priority", "Medium"), 1))
		
		# Department
		dept = getattr(doc, "department", "")
		if "department" in self.label_encoders:
			try:
				dept_encoded = self.label_encoders["department"].transform([dept])[0]
			except:
				dept_encoded = 0
		else:
			dept_encoded = 0
		features.append(dept_encoded)
		
		return features
	
	def _calculate_weekly_trend(self, df, date_field):
		"""Calculate weekly trend"""
		df["week"] = df[date_field].dt.isocalendar().week
		weekly_counts = df.groupby("week").size().to_dict()
		# Convert keys and values to int
		return {int(k): int(v) for k, v in weekly_counts.items()}
	
	def _calculate_growth_rate(self, df, date_field):
		"""Calculate growth rate"""
		df = df.sort_values(date_field)
		first_half = df.iloc[:len(df)//2]
		second_half = df.iloc[len(df)//2:]
		
		if len(first_half) == 0:
			return 0.0
		
		growth_rate = ((len(second_half) - len(first_half)) / len(first_half)) * 100
		return float(round(growth_rate, 2))


@frappe.whitelist()
def predict_response_time_api(doctype, docname):
	"""API to predict response time"""
	analytics = CorrespondenceAnalytics()
	return analytics.predict_response_time(doctype, docname)


@frappe.whitelist()
def predict_priority_api(doctype, docname):
	"""API to predict priority"""
	analytics = CorrespondenceAnalytics()
	return analytics.predict_priority(doctype, docname)


@frappe.whitelist()
def analyze_trends_api(doctype, period_days=90):
	"""API to analyze trends"""
	analytics = CorrespondenceAnalytics()
	return analytics.analyze_trends(doctype, int(period_days))


@frappe.whitelist()
def identify_bottlenecks_api(doctype):
	"""API to identify bottlenecks"""
	analytics = CorrespondenceAnalytics()
	return analytics.identify_bottlenecks(doctype)


@frappe.whitelist()
def generate_insights_api(doctype):
	"""API to generate insights"""
	analytics = CorrespondenceAnalytics()
	return analytics.generate_insights(doctype)


@frappe.whitelist()
def get_analytics_dashboard(doctype):
	"""
	Get comprehensive analytics dashboard data
	
	Args:
		doctype: Document type
		
	Returns:
		dict: Dashboard data
	"""
	analytics = CorrespondenceAnalytics()
	
	return {
		"trends": analytics.analyze_trends(doctype, 30),
		"bottlenecks": analytics.identify_bottlenecks(doctype),
		"insights": analytics.generate_insights(doctype)
	}
