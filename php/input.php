<?php
// menggunakan mysqli
include 'koneksi.php';
$nama = $_POST['nama'];
$tanggal = date('Y-m-d', strtotime($_POST['waktu']));
$jam = date('H:i:s', strtotime($_POST['waktu']));
$jam_only = date('H:i', strtotime($_POST['waktu']));
if($nama != null || $nama != ''){
    $check = mysqli_query($koneksi, "SELECT * FROM absen WHERE nama='$nama' AND tanggal='$tanggal' AND jam like '$jam_only%'");
    if(mysqli_num_rows($check) > 0){
        echo 'sudah';
    }else{
        $result = mysqli_query($koneksi, "INSERT INTO absen VALUES(null,'$nama','$tanggal','$jam')");
        
        if ($result) {
            echo 'berhasil';
        } else {
            echo 'gagal';
        }
    }
}else{
    echo 'gagal';
}
