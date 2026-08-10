# Hilti-SLAM-Challenge-2022
[<img src="https://img.shields.io/badge/Home_Page-red" alt="Home Page">](https://hilti-challenge.com/dataset-2022)
[<img src="https://img.shields.io/badge/🤗%20Hugging%20Face-Dataset-yellow" alt="Hugging Face Dataset">](https://huggingface.co/datasets/Hilti-Research/hilti-slam-challenge-2022)
[<img src="https://img.shields.io/badge/arXiv-2208.09825-b31b1b" alt="arXiv">](https://arxiv.org/abs/2208.09825)

![HSC2022](doc/HSC2022.jpg?raw=true)


# FAQ

## Which datasets should be submitted for the challenge?
The more datasets you submit the more points you can get. The datasets where we provide the groundtruth are not considered in the final score.

## If we submit the result, are you going to disclose the name of all the participants?
We disclose the names only after prior approval. Before making the leaderboard public I will send out an email to all participants with their respective rank and the option to withdraw.

## How are the results scored?
The submission will be ranked based on the completeness of the trajectory as well as on the position accuracy (ATE). The score is based on the ATE of individual points on the trajectory. Depending on the error between 10 and 0 points are added to your final score. This way also incomplete trajectories can be included in the evaluation. You always can submit your current results and receive an accuracy report using our [submission system](https://submit.hilti-challenge.com/). 

## Is the ground truth available?
We provide ground truth for all sequences. We also provide high-accuracy laserscans for selected datasets.

## We noticed that the timestamp for every point in a lidar point cloud scan is equal. Is it possible to correct this issue?
The Hesai ros driver stores the timestamp in this [struct](https://github.com/HesaiTechnology/HesaiLidar_General_ROS/blob/master/src/HesaiLidar_General_SDK/src/PandarGeneralRaw/include/pandarGeneral/point_types.h). What happens is the `sensor_msgs/PointCloud2` Message has a "data" member in byte and it stores the `PointXYZIT` defined time, xyz, etc. The "field" member describes what type of info is in "data". In a programme, one would convert the `PointCloud2` msg into `PointXYZIT` msg to access all the element pandar records. 

## How are the frames defined on the sensor setup?
Below is a schematic of the reference frames (red = x, green = y, blue = z):
![PhasmaFrames](doc/phasma_frames.png)
The frames are:
- `C0` to `C4` are the camera frames of the alphasense.
- `I` is the IMU frame as installed on the alphasense. Note that this is also the same frame the ground truth is defined in.
- `T` is the tip frame. A calibration between IMU and tip is provided.

## Is there a URDF model of the sensor setup?
Yes, now there is! You can clone and compile the following ROS packages:
- [`phasma_description`](https://github.com/Hilti-Research/phasma_description.git): this is the main URDF model of the sensor setup.
- [`hesai_description`](https://github.com/Hilti-Research/hesai_description): this is the URDF model of the HESAI. It's a dependency of `phasma_description`.
- [`alphasense_description`](https://github.com/Hilti-Research/alphasense_description): this is the URDF of the Alphasense. It's a dependency of `phasma_description`.

To have them in you system you can just clone and compile them in your catkin workspace, for example:
```
cd ~/catkin_ws/src/
git clone https://github.com/Hilti-Research/phasma_description.git
git clone https://github.com/Hilti-Research/hesai_description.git
git clone https://github.com/Hilti-Research/alphasense_description.git
cd ..
catkin build phasma_description
```
---
Citation
```bibtex
@article{zhang2023hilti,
  author  = {Lintong Zhang and Michael Helmberger and Lanke Frank Tarimo Fu and David Wisth and Marco Camurri and Davide Scaramuzza and Maurice Fallon},
  title   = {Hilti-Oxford Dataset: A Millimeter-Accurate Benchmark for Simultaneous Localization and Mapping},
  journal = {IEEE Robotics and Automation Letters},
  volume  = {8},
  number  = {1},
  pages   = {408--415},
  year    = {2023},
  doi     = {10.1109/LRA.2022.3226077}
}
```