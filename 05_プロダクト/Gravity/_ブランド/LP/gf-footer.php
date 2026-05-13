<div class="l-footer">
        <div class="l-contact">
            <h3 class="c-sub_ttl">Contact</h3>
            <p class="txt">
                まずは、あなたの"引力"を解剖する。<br>経営者を本来の自分に戻す。お気軽にご相談ください
            </p>
            <div class="l-contact_btn d-flex flex-center">
                <a href="<?php echo home_url() ?>/contact" class="c-btn d-flex flex-center align-center">
                    <span>問い合わせ</span>
                    <span class="d-flex">
                        <svg xmlns="http://www.w3.org/2000/svg" width="21" height="8" viewBox="0 0 21 8" fill="none">
                            <path d="M20.3536 4.35355C20.5488 4.15829 20.5488 3.84171 20.3536 3.64644L17.1716 0.464465C16.9763 0.269202 16.6597 0.269202 16.4645 0.464465C16.2692 0.659727 16.2692 0.976309 16.4645 1.17157L19.2929 4L16.4645 6.82843C16.2692 7.02369 16.2692 7.34027 16.4645 7.53553C16.6597 7.73079 16.9763 7.73079 17.1716 7.53553L20.3536 4.35355ZM0 4L4.37114e-08 4.5L20 4.5L20 4L20 3.5L-4.37114e-08 3.5L0 4Z" fill="black"/>
                        </svg>
                    </span>
                </a>
            </div>
        </div>
        <div class="footer">
            <div class="footer_logo" style="display: flex; flex-direction: column; align-items: flex-start;">
                <a href="/" class="d-flex"><span class="footer-logo__text">GrowthFix</span></a>
            </div>
            <div class="menu d-flex flex-row flex-between">
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/profile" class="menu_btn">代表者プロフィール</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/news" class="menu_btn">お知らせ</a>
                    </li>
                </ul>
                <ul class="menu_list head">
                    <li class="menu_link">個人軸（経営者自身）</li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-code/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity CODE</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-coaching/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Coaching</a>
                    </li>
                </ul>
                <ul class="menu_list head">
                    <li class="menu_link">組織軸（経営者×組織）</li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-scan/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Scan</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-recruit/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Recruit</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-cultivate/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Cultivate</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-orbit/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Orbit</a>
                    </li>
                </ul>
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/achievement" class="menu_btn">事例・実績</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/knowledge" class="menu_btn">ナレッジ</a>
                    </li>
                </ul>
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/contact" class="menu_btn">お問い合わせ</a>
                    </li>
                </ul>
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/privacy-policy/" class="menu_btn">プライバシーポリシー</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/terms/" class="menu_btn">利用規約</a>
                    </li>
                </ul>
            </div>
            <p class="copyright">Copyrights by GrowthFix. All rights reserved.</p>
        </div>
    </div>
    <?php wp_footer(); ?>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.js"></script>
    <script src="<?php echo get_template_directory_uri()?>/assets/js/wow.min.js"></script>
    <script src="<?php echo get_template_directory_uri()?>/assets/js/bundle.js"></script>
    <script src="<?php echo get_template_directory_uri()?>/assets/js/common.js"></script>

    <script>
        new WOW().init();
    </script>

</body>

</html>