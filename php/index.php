<!DOCTYPE html>
<html>

<head>
    <title>ABSEN WAJAH PYTHON PHP</title>
</head>

<body>

    <h2>DATA ABSEN</h2>
    <br />
    <button onclick="return startAbsen()">Jalankan Absen</button>
    <button onclick="return regisAbsen()">Daftarkan User</button>
    <br />
    <br />
    <table border="1">
        <thead>
            <tr>
                <th>NO</th>
                <th>Nama</th>
                <th>Tanggal</th>
                <th>Jam</th>
            </tr>
        </thead>
        <tbody id="list_data_absen">
        </tbody>
    </table>

    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js">
    </script>

    <script type="text/javascript" language="javascript">
        function startAbsen() {
            <?php
            $command = escapeshellcmd('python python/absen.py');
            $output = shell_exec($command);
            ?>
            console.log('<?= $output ?>');
        }

        function regisAbsen() {
            $.ajax({
                type: "GET",
                url: "python/regis_faces.py",
                success: function() {
                    console.log('menjalankan registrasi');
                }
            });
        }

        $(document).ready(function() {
            setInterval(function() {
                $.get(
                    "getData.php",
                    function(data) {
                        $('#list_data_absen').html(data);
                    });
            });
        }, 1000);
    </script>

</body>

</html>