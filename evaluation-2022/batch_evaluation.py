#!/usr/bin/env python3


import glob
from tqdm import tqdm
from evaluation import evaluate
import pandas as pd
import os
import numpy as np
import dataframe_image as dfi
from PIL import Image, ImageDraw, ImageFont
import sys
from evo.tools import file_interface


def evaluate_submission(submission_directory, reference_directory, verbose=True):
    """
    evaluates a submission, the results are stored in result.csv, a png for every dataset and a final calculated score (returned and stored in score.png)
    :param submission_directory:
    :param reference_directory:
    :return: total calculated score
    """
    datasets_to_check = [

        # new format
        "exp01_construction_ground_level.txt",
        "exp02_construction_multilevel.txt",
        "exp03_construction_stairs.txt",
        "exp04_construction_upper_level.txt",
        "exp05_construction_upper_level_2.txt",
        "exp06_construction_upper_level_3.txt",
        "exp07_long_corridor.txt",
        "exp09_cupola.txt",
        "exp11_lower_gallery.txt",
        "exp15_attic_to_upper_gallery.txt",
        "exp21_outside_building.txt"
    ]

    datasets_exclude_score=[
        "exp04_construction_upper_level.txt",
        "exp05_construction_upper_level_2.txt",
        "exp06_construction_upper_level_3.txt"

    ]

    submission_folder_name = os.path.basename(os.path.normpath(submission_directory))
    results_file = os.path.join(submission_directory, "results.csv")
    submission_files = glob.glob(submission_directory + '/**/*.txt', recursive=True)

    # rename submission files if they are in old format
    for file in submission_files:
        directory = os.path.dirname(file)
        basename = os.path.basename(file)
        if basename == 'exp_04_construction_upper_level_easy_2_2022-03-03-11-48-59.txt':
            new_file = os.path.join(directory, "exp04_construction_upper_level.txt")
            os.rename(file, new_file)
        elif basename == 'exp_05_construction_upper_level_easy_2022-03-03-11-46-10.txt':
            new_file = os.path.join(directory, "exp05_construction_upper_level_2.txt")
            os.rename(file, new_file)
        elif basename == 'exp_06_construction_upper_level_hard_2022-03-03-12-08-37.txt':
            new_file = os.path.join(directory, "exp06_construction_upper_level_3.txt")
            os.rename(file, new_file)
    submission_files = glob.glob(submission_directory + '/**/*.txt', recursive=True)

    if len(submission_files) == 0:
        raise Exception('No .txt files to evaluate in submission')

    # tmp = tmp +1
    # if tmp > 3:
    #     break

    dataset = []
    rmse = []
    mean = []
    median = []
    std = []
    minimum = []
    maximum = []
    sse = []
    points_estimate = []
    points_reference = []
    completeness = []
    scores = np.zeros((len(datasets_to_check), 6), float)
    all_errors = np.empty((1), float)

    for idx, reference in enumerate(tqdm(datasets_to_check, 'datasets', leave=False, disable=not verbose)):
        submission_name = reference
        submission_file = ''

        for file in submission_files:
            path, filename = os.path.split(file)
            filename = filename[0:-4]  # cut off extension
            if reference.lower().find(filename.lower()) >= 0:
                submission_file = file

        if len(submission_file) < 1:
            dataset.append(submission_name)
            rmse.append(None)
            mean.append(None)
            median.append(None)
            std.append(None)
            minimum.append(None)
            maximum.append(None)
            sse.append(None)
            points_estimate.append(None)
            points_reference.append(None)
            completeness.append(0)
            if verbose:
                print("\nno fitting file for {} could be found!".format(
                    submission_directory + "/" + submission_name + "*.txt"))
        else:
            est_file = submission_file
            ref_file = os.path.join(reference_directory, reference)

            try:
                ape_stats, dense_trajectory, traj_est_aligned, traj_ref = evaluate(est_file, ref_file, submission_directory)
            except:
                dataset.append(submission_name)
                rmse.append(None)
                mean.append(None)
                median.append(None)
                std.append(None)
                minimum.append(None)
                maximum.append(None)
                sse.append(None)
                points_estimate.append(None)
                points_reference.append(None)
                completeness.append(0)
                print("\ntimestamp issue in {}".format(submission_file))
                continue

            dataset.append(submission_name)
            rmse.append(ape_stats["rmse"])
            mean.append(ape_stats["mean"])
            median.append(ape_stats["median"])
            std.append(ape_stats["std"])
            minimum.append(ape_stats["min"])
            maximum.append(ape_stats["max"])
            sse.append(ape_stats["sse"])
            points_estimate.append(traj_est_aligned.get_infos()['nr. of poses'])
            if dense_trajectory:
                points_reference.append(int(traj_ref.get_infos()['duration (s)'] * 10))
            else:
                points_reference.append(traj_ref.get_infos()['nr. of poses'])
                # only works with sparse traj.
                all_pts = np.c_[traj_ref.positions_xyz[:traj_est_aligned.positions_xyz.shape[0],
                                :], traj_est_aligned.positions_xyz]
                diff = np.linalg.norm(traj_ref.positions_xyz[:traj_est_aligned.positions_xyz.shape[0],
                                      :] - traj_est_aligned.positions_xyz, axis=1)
                all_errors = np.r_[all_errors, diff]

                # compute score
                pts_per_bin = [10, 6, 3, 1, 0]
                accuracy_boundaries = [1.0 * 1e-2, 3 * 1e-2, 6 * 1e-2, 10 * 1e-2, 999999.0 * 1e-2]

                bin_1 = [i for i in diff if i < accuracy_boundaries[0]]
                bin_2 = [i for i in diff if i >= accuracy_boundaries[0] and i < accuracy_boundaries[1]]
                bin_3 = [i for i in diff if i >= accuracy_boundaries[1] and i < accuracy_boundaries[2]]
                bin_4 = [i for i in diff if i >= accuracy_boundaries[2] and i < accuracy_boundaries[3]]
                bin_5 = [i for i in diff if i >= accuracy_boundaries[3]]

                current_score = len(bin_1) * pts_per_bin[0] + len(bin_2) * pts_per_bin[1] + len(bin_3) * \
                                pts_per_bin[2] + len(bin_4) * pts_per_bin[3] + len(bin_5) * pts_per_bin[4]
                # exponential scoring method
                a, c = 12.91549665, 25.58427881
                exponential_score = 0

                for point in diff:
                    exponential_score+=exp_score(point,a,c)
                num_poses=file_interface.read_tum_trajectory_file(ref_file).num_poses
                # normalize score
                current_score=current_score/(num_poses/10)
                # remove score if it is one of the datasets that have been published before
                if reference in datasets_exclude_score:
                    current_score=None

                scores[idx, :] = [len(bin_1), len(bin_2), len(bin_3), len(bin_4), len(bin_5), current_score]

            completeness.append(min(points_estimate[-1] / points_reference[-1], 1))

    data = {'dataset': dataset, "rmse": rmse, "mean": mean, "median": median, "std": std, "min": minimum,
            "max": maximum, "sse": sse, "points_estimate": points_estimate, "points_reference": points_reference,
            "completeness": completeness, "score": scores[:, 5].tolist()}
    df = pd.DataFrame(data=data)
    df2 = df.copy()
    df2.loc['Result'] = df.mean(numeric_only=True, axis=0)

    df2.at['Result', 'points_estimate'] = df['points_estimate'].sum()
    df2.at['Result', 'points_reference'] = df['points_reference'].sum()
    df2.at['Result', 'score'] = df['score'].sum()
    df2.to_csv(results_file, index=True)

    # save all errors (only for debug)
    # np.savetxt(os.path.join(submission_folder,submission_folder_name + "_all_errors.csv"), all_errors, delimiter=",")

    # generate score image
    df_score = pd.DataFrame(
        {'< 1cm': scores[:, 0], '< 3cm': scores[:, 1], '< 6cm': scores[:, 2], '< 10cm': scores[:, 3],
         '> 10cm': scores[:, 4],
         'Score': scores[:, 5]})
    # Change the row indexes
    df_score.index = [i[:5] for i in dataset]

    total = df_score.sum()
    total.name = 'Total'
    # Assign sum of all rows of DataFrame as a new Row
    df_score = df_score.append(total.transpose())
    # df_score = df_score.sort_index()
    df_score_formated=df_score.style.format(precision=2,formatter={('Score'): "{:.2f}"},na_rep="-")
    dfi.export(df_score_formated, os.path.join(submission_directory, "./score.png"), table_conversion="matplotlib",fontsize=17)
    return total

def exp_score(x,a, c):
    result= a*np.exp(-c*x)
    if result>10:
        return 10
    else:
        return result

def get_concat_v_blank(im1, im2, color=(255, 255, 255)):
    """
    stacks 2 images vertically while filling empty space with a color (white by default)
    :param im1: first image
    :param im2: second image
    :param color: color for empty space
    :return: stacked image
    """
    dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color)
    x_origin = int((im2.width - im1.width) / 2)
    dst.paste(im1, (x_origin, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def combine_pictures(path, name, save_image=True):
    """
    takes all .png in a given path and combines them to a resulting image.
    :param path: path of the directory
    :param name: title displayed on the combined image.
    :param save_image: if set to True, will save the resulting image to path + "/combined.png"
    :return: combined image
    """

    initial_image = Image.open(path + "/score.png")

    image_paths = set(glob.glob(path + "/*.png")) - set(glob.glob(path + "/*score*")) - set(
        glob.glob(path + "/combine*"))
    image_paths = list(image_paths)
    image_paths.sort()
    for i in image_paths:
        image = Image.open(i)
        initial_image = get_concat_v_blank(initial_image, image)
    W, H = 1400, 200
    Title_image = Image.new('RGB', (W, H), color=(255, 255, 255))
    font = ImageFont.truetype("fonts/calibri.ttf", 100)
    draw = ImageDraw.Draw(Title_image)
    w, h = font.getsize(name)
    draw.text(((W - w) / 2, (H - h) / 2), name, (0, 0, 0), font=font)
    initial_image = get_concat_v_blank(Title_image, initial_image)

    if save_image:
        initial_image.save(path + "/combined.png")

    return initial_image


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f'Usage: ./batch_evaluation.py submission_path output_path groundtruth_path', file=sys.stderr)

        # exit(1)
        # debugging

        submission_path = "/your/path/to/submissions"
        output_path = "/your/path/to/output"
        groundtruth_path = "/your/path/to/groundtruth_2022"

    else:
        submission_path = sys.argv[1]
        output_path = sys.argv[2]
        groundtruth_path = sys.argv[3]

    for d in [submission_path, output_path, groundtruth_path]:
        if not os.path.isdir(d):
            print(f'No such directory: {d}', file=sys.stderr)
            exit(1)

    evaluate_submission(submission_path, groundtruth_path)
    combine_pictures(submission_path, os.path.basename(submission_path))

    # move output file to output directory
    pngs = glob.glob(submission_path + "/*.png")
    csvs = glob.glob(submission_path + "/*.csv")
    for f in pngs + csvs:
        print(f)
        os.rename(f, f'{output_path}/{os.path.basename(f)}')
