from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='image2pipe_gpu',
    version='0.1.10',
    author='Anton P. Linevich',
    author_email='anton@linevich.com',
    keywords="ffmpeg yuv image2pipe_gpu",
    packages=['image2pipe_gpu', ],
    scripts=[],
    url='https://github.com/sondv7/image2pipe_gpu',
    license='LICENSE.txt',
    description='Simple ffmpeg wrapper for image2pipe_gpu which yields rawvideo frames from input video URL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['tblib', 'numpy', 'websocket'],
    python_requires='>=3.2',
)
