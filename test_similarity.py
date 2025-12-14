#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import frappe
from frappe import _

def test_similarity():
    """Test the similarity engine"""
    frappe.init(site='erp.localhost')
    frappe.connect()
    
    try:
        from correspondence.correspondence.utils.similarity_engine import get_similar_documents
        
        # Get first incoming letter
        letters = frappe.get_all("Incoming Letter", limit=1)
        if not letters:
            print("No incoming letters found")
            return
        
        letter_name = letters[0].name
        print(f"Testing with letter: {letter_name}")
        
        result = get_similar_documents("Incoming Letter", letter_name)
        print(f"Result: {result}")
        
        if result.get("success"):
            print(f"Found {len(result.get('documents', []))} similar documents")
            for doc in result.get('documents', []):
                print(f"  - {doc.get('name')}: {doc.get('score')}")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()

if __name__ == "__main__":
    test_similarity()
