import argparse
import sys
import os

current_file_level = 3
current_dir = os.path.dirname(os.path.realpath(__file__))
for _ in range(current_file_level):
    current_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)

from rck.utils.scn.process import get_haploid_scnt
from rck.core.io import get_logging_cli_parser, get_standard_logger_from_args, read_scnt_from_source, write_scnt_to_shatterseek_destination
from rck.utils.adj.process import get_chromosome_strip_parser


def main():
    parser = argparse.ArgumentParser(prog="RCK-UTILS-SCNT-rck2x")
    cli_logging_parser = get_logging_cli_parser()
    chr_strip_parser = get_chromosome_strip_parser()
    subparsers = parser.add_subparsers(title="command", dest="command")
    subparsers.required = True
    ####
    shatterseek_parser = subparsers.add_parser("shatterseek", parents=[cli_logging_parser, chr_strip_parser])
    shatterseek_parser.add_argument("rck_scnt", type=argparse.FileType("rt"), default=sys.stdin)
    shatterseek_parser.add_argument("--clone-id", required=True)
    shatterseek_parser.add_argument("--separator", default="\t")
    shatterseek_parser.add_argument("--extra-separator", default=";")
    shatterseek_parser.add_argument("--default-cn", type=int, default=0)
    shatterseek_parser.add_argument("--output-header", action="store_true", dest="output_header")
    shatterseek_parser.add_argument("-o", "--output", type=argparse.FileType("wt"), default=sys.stdout)
    ####
    args = parser.parse_args()
    logger = get_standard_logger_from_args(args=args, program_name="RCK-UTILS-SCNT")

    if args.command == "shatterseek":
        logger.info("Starting converting RCK Segment Copy Number Tensor data to ShatterSeek")
        logger.debug("Specified clone is {clone_id}".format(clone_id=args.clone_id))
        logger.info("Reading RCK formatted data from {file}".format(file=args.rck_scnt))
        segments, scnt = read_scnt_from_source(source=args.rck_scnt, separator=args.separator, extra_separator=args.extra_separator)
        logger.info("Read CN data is translated into a haploid (!!!) version of itself.")
        haploid_scnt = get_haploid_scnt(segments=segments, scnt=scnt)
        logger.info("Writing data for clone {clone_id} in a ShatterSeek suitable format to {file}".format(clone_id=args.clone_id, file=args.output))
        write_scnt_to_shatterseek_destination(destination=args.output, segments=segments, scnt=haploid_scnt, clone_id=args.clone_id,
                                              default=args.default_cn, output_header=args.output_header)
    logger.info("Success!")


if __name__ == "__main__":
    main()