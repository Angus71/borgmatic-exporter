import json
import os

import arrow
import pytest

from src import metrics

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


class TestJsonMetrics:

    @pytest.fixture(scope="function")
    def json_content(self, mocker):
        with open(f"{PROJECT_ROOT}/data/repo-info.json") as j:
            ri = json.load(j)

        with open(f"{PROJECT_ROOT}/data/list-info.json") as j:
            li = json.load(j)

        mocker.patch("src.metrics.run_command", side_effect=[ri, li])

        yield metrics.collect_json(["/conf/foo.yaml", "/conf/bar.yaml", "/conf/baz.yaml"])

    @pytest.mark.parametrize(
        "metric, repo, expect",
        [
            ("borg_total_backups", "/borg/backup-1", 2.0),
            ("borg_total_backups", "/borg/backup-3", 0.0),
            ("borg_total_chunks", "/borg/backup-1", 3505.0),
            ("borg_total_compressed_size", "/borg/backup-1", 3965903861.0),
            ("borg_total_compressed_size_human", "/borg/backup-1", "3.7 GiB"),
            ("borg_total_size", "/borg/backup-1", 8446787072.0),
            ("borg_total_size_human", "/borg/backup-1", "7.9 GiB"),
            ("borg_total_deduplicated_compressed_size", "/borg/backup-1", 537932015.0),
            ("borg_total_deduplicated_compressed_size_human", "/borg/backup-1", "513.0 MiB"),
            ("borg_total_deduplicated_size", "/borg/backup-1", 1296544339.0),
            ("borg_total_deduplicated_size_human", "/borg/backup-1", "1.2 GiB"),
            ("borg_total_deduplicated_size", "/borg/backup-2", 21296544339.0),
            ("borg_total_deduplicated_size_human", "/borg/backup-2", "19.8 GiB"),
            ("borg_last_backup_duration", "/borg/backup-1", 107.499993),
            ("borg_last_backup_duration", "/borg/backup-2", 117.189547),
            ("borg_last_backup_files", "/borg/backup-1", 11),
            ("borg_last_backup_files", "/borg/backup-2", 12),
            (
                "borg_last_backup_deduplicated_compressed_size",
                "/borg/backup-1",
                10351331,
            ),
            (
                "borg_last_backup_deduplicated_compressed_size",
                "/borg/backup-2",
                18718565,
            ),
            ("borg_last_backup_compressed_size", "/borg/backup-1", 379050627),
            ("borg_last_backup_compressed_size_human", "/borg/backup-1", "361.5 MiB"),
            ("borg_last_backup_compressed_size", "/borg/backup-2", 419966002),
            ("borg_last_backup_compressed_size_human", "/borg/backup-2", "400.5 MiB"),
            ("borg_last_backup_size", "/borg/backup-1", 807712494),
            ("borg_last_backup_size_human", "/borg/backup-1", "770.3 MiB"),
            ("borg_last_backup_size", "/borg/backup-2", 893501335),
            ("borg_last_backup_size_human", "/borg/backup-2", "852.1 MiB"),
        ]
    )
    def test_individual_metrics(self, json_content, metric, repo, expect):
        # Check for repo
        assert [r for r in json_content if r['location'] == repo][0][metric] == expect

    def test_timestamp_metrics(self, json_content):
        assert arrow.get([r for r in json_content if r['location'] == "/borg/backup-1"][0]["borg_last_backup_timestamp"])