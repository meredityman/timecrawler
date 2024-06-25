from setuptools import setup, find_packages

setup(name='timecrawler',
      version='0.0',
      description='',
      url='https://github.com/meredityman/timecrawler',
      author='Meredith Thomas',
      author_email='meredityman@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
            "certifi>=2024.2.2",
            "charset-normalizer>=3.3.2",
            "idna>=3.7",
            "isodate>=0.6.1",
            "pillow>=10.3.0",
            "pyparsing>=3.1.2",
            "rdflib>=7.0.0",
            "requests>=2.32.2",
            "six>=1.16.0",
            "SPARQLWrapper>=2.0.0",
            "urllib3>=2.2.1",
            "huggingface_hub>=0.23.0",
            # "llama_cpp_python>=0.2.79"
      ]
    )