from blog.models import BlogCategory, BlogPost
from django.contrib.auth.models import User
from django.utils import timezone

# Create or get admin user
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'limbsorthopaedic@gmail.com', 'admin')

# Create blog categories
BlogCategory.objects.all().delete()
cat1 = BlogCategory.objects.create(
    name='Orthopaedic Conditions',
    description='Information about various orthopaedic conditions and treatments',
    slug='orthopaedic-conditions'
)
cat2 = BlogCategory.objects.create(
    name='Living with Prosthetics',
    description='Tips and stories for those living with prosthetic limbs',
    slug='living-with-prosthetics'
)
cat3 = BlogCategory.objects.create(
    name='News & Events',
    description='Latest news and upcoming events at LIMBS Orthopaedic',
    slug='news-events'
)

# Create blog posts
BlogPost.objects.all().delete()

post1 = BlogPost.objects.create(
    title='Understanding Rickets: Causes, Symptoms and Treatment',
    slug='understanding-rickets',
    author=admin_user,
    content="""<h2>What is Rickets?</h2>
<p>Rickets is a condition that affects bone development in children. It causes bone pain, poor growth and soft, weak bones that can lead to bone deformities.</p>

<h2>Causes of Rickets</h2>
<p>The most common cause of rickets is a lack of vitamin D or calcium in a child's diet. Vitamin D plays a crucial role in the absorption of calcium from food, which is essential for developing strong and healthy bones.</p>

<h2>Symptoms of Rickets</h2>
<p>Common symptoms include:</p>
<ul>
<li>Pain in the spine, pelvis, and legs</li>
<li>Delayed growth and development</li>
<li>Muscle weakness</li>
<li>Dental problems</li>
<li>Skeletal deformities such as bowed legs or knock knees</li>
</ul>

<h2>Treatment Options</h2>
<p>Treatment for rickets typically involves increasing vitamin D and calcium intake through diet modifications and supplements. In some cases, specially designed braces may be used to correct bone deformities. Early intervention is key to preventing long-term complications.</p>

<p>At LIMBS Orthopaedic, we provide comprehensive assessment and management strategies for children with rickets. Our approach includes nutritional guidance, corrective orthotic solutions, and ongoing support to ensure optimal bone development.</p>""",
    summary='Learn about the causes, symptoms, and treatment options for rickets, a condition affecting bone development in children.',
    status='published',
    published_date=timezone.now()
)
post1.categories.add(cat1)

post2 = BlogPost.objects.create(
    title='Advancements in Prosthetic Technology: What\'s New in 2024',
    slug='advancements-in-prosthetic-technology-2024',
    author=admin_user,
    content="""<h2>The Evolution of Prosthetics</h2>
<p>Prosthetic technology has come a long way from the wooden legs of ancient civilizations. Today's prosthetic limbs incorporate cutting-edge materials, sophisticated electronics, and even neural interfaces.</p>

<h2>Latest Innovations</h2>
<p>Some of the most exciting recent developments include:</p>
<ul>
<li><strong>Bionic Limbs:</strong> Prosthetics that can be controlled by thought using neural interfaces</li>
<li><strong>3D Printed Prosthetics:</strong> Custom, affordable solutions that can be rapidly produced</li>
<li><strong>Smart Materials:</strong> Prosthetics that adapt to different temperatures and activities</li>
<li><strong>Sensory Feedback Systems:</strong> Technology that allows users to "feel" through their prosthetic limb</li>
</ul>

<h2>Impact on Quality of Life</h2>
<p>These technological advancements are transforming lives by providing more natural movement, greater comfort, and enhanced functionality. Users report improved confidence, independence, and overall well-being.</p>

<p>At LIMBS Orthopaedic, we stay at the forefront of prosthetic technology to offer our patients the most effective solutions for their needs. Our team works closely with each individual to find the right balance of technology, comfort, and functionality.</p>""",
    summary='Discover the latest technological innovations in prosthetic limbs and how they are improving quality of life for users.',
    status='published',
    published_date=timezone.now()
)
post2.categories.add(cat2)

post3 = BlogPost.objects.create(
    title='Caring for Your Child\'s Orthotic Devices: A Parent\'s Guide',
    slug='caring-for-child-orthotic-devices',
    author=admin_user,
    content="""<h2>The Importance of Proper Orthotic Care</h2>
<p>Orthotic devices play a crucial role in correcting or supporting your child's bone and muscle development. Proper care ensures these devices remain effective, comfortable, and durable.</p>

<h2>Daily Maintenance Tips</h2>
<p>Follow these guidelines to keep your child's orthotics in good condition:</p>
<ul>
<li><strong>Cleaning:</strong> Wipe down devices daily with a damp cloth and mild soap</li>
<li><strong>Inspection:</strong> Regularly check for signs of wear, cracks, or loose parts</li>
<li><strong>Proper Application:</strong> Ensure devices are correctly positioned according to your specialist's instructions</li>
<li><strong>Skin Care:</strong> Monitor your child's skin for signs of irritation or pressure sores</li>
</ul>

<h2>When to Contact Your Specialist</h2>
<p>Reach out to your orthotic specialist if:</p>
<ul>
<li>The device no longer fits properly due to your child's growth</li>
<li>You notice persistent skin irritation or discomfort</li>
<li>The device becomes damaged or broken</li>
<li>Your child's condition or symptoms change</li>
</ul>

<p>At LIMBS Orthopaedic, we provide ongoing support for families using our orthotic devices. Regular follow-up appointments are essential to ensure the device continues to meet your child's changing needs as they grow and develop.</p>""",
    summary='Essential tips for parents on how to maintain and monitor orthotic devices for optimal effectiveness and comfort.',
    status='published',
    published_date=timezone.now()
)
post3.categories.add(cat1)

print('Blog categories and posts created successfully')