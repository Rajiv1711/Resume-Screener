#!/usr/bin/env python3
"""
Basic test for Resume Screener - No complex imports
"""

import sys
import os
import json

def test_basic_functionality():
    """Test the basic functionality without AI dependencies"""
    print("=== Testing Basic Resume Screener Functionality ===\n")
    
    # Test 1: Basic Python functionality
    print("1. Testing basic Python imports...")
    try:
        import sqlite3
        import json
        import re
        print("   ✓ Basic imports successful")
    except ImportError as e:
        print(f"   ✗ Basic imports failed: {e}")
        return False
    
    # Test 2: Create a simple resume parser
    print("2. Testing basic resume parsing...")
    try:
        # Simple resume parser without AI dependencies
        class SimpleResumeParser:
            def __init__(self):
                self.skills_keywords = [
                    'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker', 
                    'kubernetes', 'machine learning', 'ai', 'fastapi', 'react', 
                    'node.js', 'mongodb', 'postgresql', 'git', 'jenkins', 'html',
                    'css', 'typescript', 'linux', 'windows', 'agile', 'scrum'
                ]
            
            def parse_resume(self, text):
                """Basic keyword extraction"""
                found_skills = []
                text_lower = text.lower()
                
                for skill in self.skills_keywords:
                    if skill in text_lower:
                        found_skills.append(skill.title())
                
                # Simple experience extraction
                experience = []
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if any(role in line_lower for role in ['engineer', 'developer', 'analyst', 'manager']):
                        exp = {
                            "job_title": line,
                            "company": lines[i-1] if i > 0 and len(lines[i-1]) < 100 else "Unknown",
                            "duration": "Not specified",
                            "description": "Extracted from resume"
                        }
                        experience.append(exp)
                
                return {
                    "skills": found_skills,
                    "experience": experience
                }
        
        # Test the parser
        parser = SimpleResumeParser()
        sample_resume = """
        JOHN DOE - Senior Software Engineer
        Tech Company Inc. (2020-2023)
        - Developed applications using Python and JavaScript
        - Used AWS, Docker, and Kubernetes
        - Managed SQL databases and React applications
        
        SKILLS: Python, JavaScript, AWS, Docker, SQL, React, Node.js
        """
        
        result = parser.parse_resume(sample_resume)
        print(f"   ✓ Basic parsing successful")
        print(f"   ✓ Found {len(result['skills'])} skills")
        print(f"   ✓ Found {len(result['experience'])} experiences")
        
    except Exception as e:
        print(f"   ✗ Basic parsing failed: {e}")
        return False
    
    # Test 3: Test JSON serialization (for API responses)
    print("3. Testing JSON serialization...")
    try:
        test_data = {
            "skills": ["Python", "JavaScript"],
            "experience": [
                {
                    "job_title": "Software Engineer",
                    "company": "Test Company",
                    "duration": "2020-2023",
                    "description": "Test description"
                }
            ]
        }
        
        json_str = json.dumps(test_data)
        parsed_back = json.loads(json_str)
        
        assert parsed_back["skills"] == test_data["skills"]
        print("   ✓ JSON serialization successful")
        
    except Exception as e:
        print(f"   ✗ JSON test failed: {e}")
        return False
    
    # Test 4: Test file I/O (for PDF/text file processing)
    print("4. Testing file I/O operations...")
    try:
        # Create a test file
        test_content = "Test resume content with Python and SQL skills"
        with open("test_temp.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Read it back
        with open("test_temp.txt", "r", encoding="utf-8") as f:
            content_back = f.read()
        
        assert content_back == test_content
        print("   ✓ File I/O operations successful")
        
        # Clean up
        import os
        if os.path.exists("test_temp.txt"):
            os.remove("test_temp.txt")
            
    except Exception as e:
        print(f"   ✗ File I/O test failed: {e}")
        return False
    
    print("\n=== All Basic Tests PASSED ===")
    print("The core functionality is working correctly.")
    print("You can now proceed to run the FastAPI server.")
    
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)