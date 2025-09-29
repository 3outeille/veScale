#!/usr/bin/env python3
"""
generate_nccl_topo_8gpu.py

Generate an NCCL topology dump (XML) using 8 GPUs.

Usage:
    python generate_nccl_topo_8gpu.py /tmp/nccl_topology.xml
"""

import os
import sys
import torch
import torch.distributed as dist

def main(out_file):
    # This script needs to be launched with torchrun
    rank = int(os.environ["RANK"])
    local_rank = int(os.environ["LOCAL_RANK"])

    if rank == 0:
        os.environ["NCCL_TOPO_DUMP_FILE"] = out_file

    if not torch.cuda.is_available():
        print("CUDA is not available. Run this on a GPU machine.")
        sys.exit(1)

    ndev = torch.cuda.device_count()
    world_size = int(os.environ["WORLD_SIZE"])
    if world_size > ndev:
        if rank == 0:
            print(f"Error: world size ({world_size}) is greater than number of GPUs ({ndev}).")
        sys.exit(1)

    torch.cuda.set_device(local_rank)

    dist.init_process_group(backend="nccl")

    dist.barrier()
    dist.destroy_process_group()

    if rank == 0:
        print(f"NCCL topology written to: {out_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: torchrun --nproc_per_node=<num_gpus> dump_topo.py <output_file>")
        sys.exit(1)
    main(sys.argv[1])
