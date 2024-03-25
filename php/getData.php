<?php
        include 'koneksi.php';
        $no = 1;
        $data = mysqli_query($koneksi, "select * from absen");
        while ($d = mysqli_fetch_array($data)) {
        echo "
            <tr>
                <td>". $no++."</td>
                <td>". $d['nama']."</td>
                <td>". $d['tanggal']."</td>
                <td>". $d['jam']."</td>
            </tr>
            ";
        }