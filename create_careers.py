
from careers.models import Career

# Clear existing careers
Career.objects.all().delete()

# Create Orthopaedic Technologist position
Career.objects.create(
    title="Orthopaedic Technologist",
    location="Kasarani, Nairobi",
    job_type="Full-time",
    industry="Healthcare",
    image_url="https://i.imgur.com/example1.jpg",
    about="""We are seeking a skilled and compassionate Orthopaedic Technologist to join our team at LIMBS Orthopaedic. The ideal candidate will have experience in providing orthopaedic care and assisting in prosthetic and orthotic services.""",
    responsibilities="""- Assist in the fabrication and fitting of prosthetic and orthotic devices
- Perform initial patient assessments and measurements
- Maintain accurate patient records and documentation
- Collaborate with the healthcare team to ensure optimal patient outcomes
- Provide patient education on device use and care""",
    requirements="""- Diploma or Degree in Orthopaedic Technology
- Valid registration with relevant medical board
- Minimum 2 years experience in orthopaedic care
- Strong communication and interpersonal skills
- Proficiency in medical documentation
- Physical stamina and ability to assist patients""",
    benefits="""- Competitive salary package
- Medical insurance coverage
- Professional development opportunities
- Flexible work schedule
- Supportive work environment
- Performance bonuses""",
    is_active=True
)

# Create Marketing Manager position
Career.objects.create(
    title="Marketing Manager",
    location="Kasarani, Nairobi",
    job_type="Full-time",
    industry="Healthcare Marketing",
    image_url="https://i.imgur.com/example2.jpg",
    about="""LIMBS Orthopaedic is looking for a dynamic Marketing Manager to lead our marketing initiatives and enhance our brand presence. The ideal candidate will have experience in healthcare marketing and a passion for making a difference.""",
    responsibilities="""- Develop and implement marketing strategies
- Manage social media presence and digital marketing campaigns
- Create engaging content for various platforms
- Analyze market trends and competitor activities
- Track and report on marketing metrics
- Organize healthcare events and workshops""",
    requirements="""- Bachelor's degree in Marketing or related field
- 3+ years experience in healthcare marketing
- Strong digital marketing skills
- Excellent project management abilities
- Creative thinking and problem-solving skills
- Knowledge of healthcare industry regulations""",
    benefits="""- Competitive salary package
- Healthcare coverage
- Professional development opportunities
- Performance bonuses
- Flexible work arrangements
- Collaborative work environment""",
    is_active=True
)

print("Career positions created successfully!")
