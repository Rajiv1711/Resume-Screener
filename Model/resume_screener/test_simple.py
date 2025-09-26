import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from parser import ZephyrResumeParser

def test_parser():
    print("Testing Zephyr Resume Parser...")
    
    parser = ZephyrResumeParser()
    
    sample_resume = """
    JOHN DOE
    Software Engineer
    Email: john.doe@email.com
    Phone: (123) 456-7890
    
    EXPERIENCE:
    Senior Software Engineer, Tech Company Inc. (Jan 2020 - Present)
    - Developed web applications using Python and FastAPI
    - Implemented machine learning models for data analysis
    - Managed AWS cloud infrastructure and Docker containers
    
    Software Developer, Startup Co. (2018 - 2020)
    - Built mobile applications with React Native
    - Designed database schemas with PostgreSQL and MongoDB
    
    SKILLS:
    Programming: Python, JavaScript, Java, SQL
    Frameworks: FastAPI, React, Node.js, Django
    Tools: AWS, Docker, Kubernetes, Git, Jenkins
    Machine Learning: Scikit-learn, TensorFlow, PyTorch
    
    EDUCATION:
    Bachelor of Computer Science, University of Technology (2014-2018)
    """
    
    print("Parsing sample resume...")
    result = parser.parse_resume(sample_resume)
    
    print("\n=== PARSING RESULTS ===")
    print(f"Skills found: {len(result.skills)}")
    for skill in result.skills:
        print(f"  - {skill}")
    
    print(f"\nExperience found: {len(result.experience)}")
    for exp in result.experience:
        print(f"  - {exp['job_title']} at {exp['company']} ({exp['duration']})")

if __name__ == "__main__":
    test_parser()